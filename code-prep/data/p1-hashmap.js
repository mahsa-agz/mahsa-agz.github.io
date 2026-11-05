pattern({
  id: 'hashmap', n: 1, name: 'هش‌مپ (Hash map)', sub: 'چیزی را که دیدی یادداشت کن',
  story: `<p><b>سال ۱۹۵۳، شرکت IBM.</b> کامپیوترها رکوردها را (مثلاً قطعه‌ها با شماره‌ی قطعه) نگه می‌داشتند و برای پیدا کردن یکی، یا باید همه را می‌گشتند یا همه را از قبل مرتب نگه می‌داشتند؛ هر دو کند. <b>هانس پیتر لون (Hans Peter Luhn)</b> در یک یادداشت داخلی ایده‌ای داد: از رقم‌های خودِ کلید، <b>آدرس</b> را حساب کن. مثلاً رقم‌ها را خرد کن و قاطی کن (اسم hash یعنی «خرد کردن و قاطی کردن»، مثل hash brown) و نتیجه را شماره‌ی کشو بگیر. اگر دو کلید در یک کشو افتادند (تصادم، collision)، در همان کشو پشت هم بگذارشان (chaining).</p>
<p>شهودش مثل <b>فهرستِ الفباییِ دفترچه تلفن</b> است: برای پیدا کردن «سارا» از صفحه‌ی اول نمی‌خوانی؛ مستقیم به برگه‌ی «س» می‌روی. تابع هش همان «حرف اول» است، فقط بهتر پخش می‌کند. هزینه‌اش؟ <b>جای اضافه</b> برای کشوها.</p>`,
  uses: `<ul>
<li><b>«آیا این را قبلاً دیده‌ام؟» در داده‌ی بزرگ</b>: «این کاربر این ویدیو را دیده؟» میان میلیاردها بازدید ← <code>set</code>، یک قدم به‌جای گشتنِ همه.</li>
<li><b>حذف تکراری‌ها</b> (dedup): <code>set(ids)</code>.</li>
<li><b>شمارش و تجمیع</b>: بازدید هر سازنده. پانداس <code>groupby</code> و SQL <code>GROUP BY</code> زیر کار همین هش را می‌سازند.</li>
<li><b>پیوند دو جدول</b>: <code>JOIN</code> در SQL و <code>merge</code> در پانداس معمولاً «hash join» هستند: یک جدول را در هش می‌ریزند و جدول دیگر را با آن جور می‌کنند.</li>
<li><b>کش (cache)</b>: جوابِ حساب‌شده را با کلیدش نگه دار (LRU Cache، پرتکرارترین سؤال تیک‌تاک).</li>
<li><b>جاهایی که خوب نیست:</b> هش <b>ترتیب</b> ندارد. «کوچک‌ترین»، «همه‌ی بین 20 تا 30»، «k تای اول» ← مرتب‌سازی، هیپ یا جست‌وجوی دودویی.</li></ul>`,
  demo: {
    title: 'Two Sum را قدم‌به‌قدم ببین',
    fields: [['nums', '2, 7, 11, 15'], ['target', '9']],
    run(f) {
      const a = nums(f.nums), t = +f.target, seen = new Map(), out = [];
      const st = () => `<span class="kv">seen = { ${[...seen].map(([k, v]) => `${k}: ${v}`).join(', ')} }</span>`;
      out.push({ cells: A(a), note: `هدف ${t}. <code>seen</code> خالی است.`, state: st() });
      for (let i = 0; i < a.length; i++) {
        const need = t - a[i];
        if (seen.has(need)) { out.push({ cells: A(a, { [seen.get(need)]: 'جفت', [i]: 'x' }, [seen.get(need), i]), note: `x = ${a[i]}، لازم: ${L(`${t} − ${a[i]} = <b>${need}</b>`)} ← در <code>seen</code> هست (اندیس ${seen.get(need)}) ← جواب <b>[${seen.get(need)}, ${i}]</b>`, state: st() }); return out; }
        out.push({ cells: A(a, { [i]: 'x' }), note: `x = ${a[i]}، لازم: <b>${need}</b> ← در <code>seen</code> نیست ← ${a[i]} را با اندیس ${i} یادداشت کن`, state: '' });
        seen.set(a[i], i); out[out.length - 1].state = st();
      }
      out.push({ cells: A(a), note: 'جفتی پیدا نشد.', state: st() });
      return out;
    }
  },
  why: `<p>یک لیست برای جواب دادن به «آیا <code>x</code> این‌جاست؟» باید همه‌ی خانه‌ها را نگاه کند: <b>O(n)</b>. هش‌مپ (<code>dict</code> / <code>set</code>) با یک تابع هش (hash function) کلید را به یک آدرس تبدیل می‌کند و مستقیم سراغ همان خانه می‌رود: به‌طور میانگین <b>O(1)</b>.</p>
<p>پس معامله ساده است: <b>حافظه خرج کن تا دیگر دنبال چیزی نگردی</b>. هر وقت راه‌حل ساده‌ات (brute force) یک حلقه‌ی داخلی دارد که فقط <i>دنبال چیزی می‌گردد</i>، از خودت بپرس: «می‌توانستم زودتر یادداشتش کنم؟»</p>
<p>سه کاربرد:</p>
<ul><li><b>جست‌وجو (Lookup):</b> چیزهایی را که دیدی نگه دار و بپرس «جفتم قبلاً آمده؟»</li>
<li><b>شمارش (Count):</b> <code>Counter</code> در یک دور تعداد هر مقدار را می‌دهد.</li>
<li><b>گروه‌بندی (Group):</b> کلید یک <i>امضا</i> است که چیزهای هم‌گروه در آن مشترک‌اند (حروف مرتب‌شده، باقیمانده، …).</li></ul>`,
  viz: `<div class="viz"><div class="vrow">${A([2, 7, 11, 15], { 1: 'x' })}</div><div class="vnote">روی <b>7</b>: لازم داریم <span dir="ltr">9 − 7 = <b>2</b></span> ← آیا 2 در <code>seen</code> هست؟ <b>بله</b> (اندیس 0) ← جواب [0, 1]</div><div class="vrow"><span class="kv">seen = { 2: 0 }</span></div></div>`,
  spot: ['«دو عضو پیدا کن که جمعشان … شود / با هم جور باشند»', '«چند بار تکرار شده / پرتکرارترین»', '«چیزهایی را که از جهتی یکسان‌اند گروه کن»', '«تکراری / یکتا / اولین غیرتکراری»', 'راه‌حل ساده‌ات دو حلقه‌ی تودرتوست و حلقه‌ی داخلی فقط <i>جست‌وجو</i> می‌کند'],
  template: String.raw`# lookup: remember, then ask
seen = {}
for i, x in enumerate(nums):
    if target - x in seen:          # partner already seen?
        return [seen[target - x], i]
    seen[x] = i                     # write it down AFTER checking

# count / group
from collections import Counter, defaultdict
cnt = Counter(nums)                 # value -> how many
groups = defaultdict(list)
for w in words:
    groups[signature(w)].append(w)`,
  tiktok: `هش‌مپ داخل خیلی از پرتکرارترین سؤال‌های تیک‌تاک پنهان است. <b>LRU Cache</b>، پرتکرارترین سؤال تیک‌تاک، یک هش‌مپ به‌اضافه‌ی لیست پیوندی است و بعداً در بخش «طراحی» می‌آید. در آزمون کدسیگنال، سؤال ۱ و ۲ اغلب با یک <code>Counter</code> حل می‌شوند.`,
  problems: [
    {
      id: 'two-sum', t: 'Two Sum', d: 'E', f: 66.5, fn: 'twoSum',
      plain: '<b>اندیس</b> دو عدد متفاوت را برگردان که جمعشان <code>target</code> شود. دقیقاً یک جواب وجود دارد.',
      hint: 'برای هر عدد <code>x</code>، چه عددی کاملش می‌کند؟ کجا می‌توانستی آن را نگه داری؟',
      idea: 'یک بار جلو برو. جفتِ <code>x</code> می‌شود <code>target − x</code>. اگر از قبل در <code>seen</code> هست، تمام. وگرنه <code>x → اندیس</code> را ذخیره کن.',
      traps: ['<b>اول</b> بررسی کن، بعد ذخیره کن تا هیچ عددی با خودش جفت نشود (<code>[3,3], 6</code> هم درست کار می‌کند چون 3ِ اول زودتر ذخیره شده).', 'مرتب کردن (sort) اندیس‌های اصلی را به هم می‌ریزد.'],
      code: String.raw`class Solution:
    def twoSum(self, nums, target):
        seen = {}                       # value -> index
        for i, x in enumerate(nums):
            if target - x in seen:
                return [seen[target - x], i]
            seen[x] = i`,
      O: 'O(n) time · O(n) space',
      tests: [[[[2, 7, 11, 15], 9], [0, 1]], [[[3, 2, 4], 6], [1, 2]], [[[3, 3], 6], [0, 1]]]
    },
    {
      id: 'group-anagrams', t: 'Group Anagrams', d: 'M', f: 45.5, fn: 'groupAnagrams', cmp: 'groups',
      plain: 'کلمه‌هایی را که از <b>همان حروف</b> ساخته شده‌اند در یک گروه بگذار («eat»، «tea»، «ate»).',
      hint: 'چه چیزی در همه‌ی جابه‌جاشده‌های یک کلمه (anagram) یکسان است؟ می‌شود کلید دیکشنری باشد؟',
      idea: 'امضا همان کلمه‌ی مرتب‌شده است: <code>"eat" → "aet"</code>. آن را کلید بگذار و هر کلمه را به گروهش اضافه کن.',
      traps: ['لیست نمی‌تواند کلید دیکشنری باشد. از رشته (<code>"".join(sorted(w))</code>) یا تاپل استفاده کن.', 'کلید سریع‌تر برای کلمه‌های بلند: تاپلی از تعداد ۲۶ حرف، یعنی O(k) به‌جای O(k log k).'],
      code: String.raw`from collections import defaultdict

class Solution:
    def groupAnagrams(self, strs):
        groups = defaultdict(list)
        for w in strs:
            groups["".join(sorted(w))].append(w)
        return list(groups.values())`,
      O: 'O(n · k log k) time, k = word length',
      tests: [[[['eat', 'tea', 'tan', 'ate', 'nat', 'bat']], [['bat'], ['nat', 'tan'], ['ate', 'eat', 'tea']]], [[['']], [['']]]]
    },
    {
      id: 'top-k-frequent-elements', t: 'Top K Frequent Elements', d: 'M', f: 66.5, fn: 'topKFrequent', cmp: 'set',
      plain: '<code>k</code> مقداری را برگردان که <b>بیشتر از همه</b> تکرار شده‌اند. ترتیب مهم نیست.',
      hint: 'اول بشمار. بعد: تعداد هیچ‌وقت از <code>n</code> بیشتر نمی‌شود. می‌شود خودِ تعداد را اندیس گرفت؟',
      idea: 'با <code>Counter</code> بشمار. سطل‌هایی بساز که <code>bucket[c]</code> مقدارهایی را نگه دارد که <code>c</code> بار آمده‌اند. سطل‌ها را از بالا به پایین بخوان تا <code>k</code> تا جمع شود.',
      traps: ['مرتب کردن همه‌ی تعدادها O(n log n) است؛ در آزمون قبول است، ولی در مصاحبه ایده‌ی سطل (bucket) را بگو.', 'راه سریعِ درست: <code>[v for v, _ in Counter(nums).most_common(k)]</code>.'],
      code: String.raw`from collections import Counter

class Solution:
    def topKFrequent(self, nums, k):
        cnt = Counter(nums)
        bucket = [[] for _ in range(len(nums) + 1)]
        for v, c in cnt.items():
            bucket[c].append(v)
        out = []
        for c in range(len(bucket) - 1, 0, -1):
            out += bucket[c]
            if len(out) >= k:
                return out[:k]`,
      O: 'O(n) time · O(n) space',
      tests: [[[[1, 1, 1, 2, 2, 3], 2], [1, 2]], [[[1], 1], [1]]]
    },
    {
      id: 'pairs-of-songs-with-total-durations-divisible-by-60', t: 'Pairs of Songs With Total Durations Divisible by 60', d: 'M', f: 34.5, fn: 'numPairsDivisibleBy60',
      plain: 'تعداد جفت آهنگ‌های <code>i &lt; j</code> را بشمار که مجموع زمانشان مضرب 60 باشد.',
      hint: 'فقط باقیمانده‌ی <code>t % 60</code> مهم است. کدام باقیمانده، باقیمانده‌ی <code>r</code> را کامل می‌کند؟',
      idea: 'همان Two Sum است روی باقیمانده‌ها، فقط به‌جای برگرداندن، <b>می‌شماری</b>. جفتِ <code>r</code> می‌شود <code>(60 − r) % 60</code>. تعداد جفت‌هایی را که تا حالا دیدی اضافه کن، بعد <code>r</code> را ثبت کن.',
      traps: ['<code>(60 − r) % 60</code> باعث می‌شود باقیمانده‌ی 0 با 0 جفت شود (نه با 60).', 'اول بشمار، بعد ثبت کن تا آهنگ با خودش جفت نشود.'],
      code: String.raw`class Solution:
    def numPairsDivisibleBy60(self, time):
        seen = [0] * 60                 # remainder -> how many so far
        pairs = 0
        for t in time:
            r = t % 60
            pairs += seen[(60 - r) % 60]
            seen[r] += 1
        return pairs`,
      O: 'O(n) time · O(1) space',
      tests: [[[[30, 20, 150, 100, 40]], 3], [[[60, 60, 60]], 3]]
    },
    {
      id: 'longest-consecutive-sequence', t: 'Longest Consecutive Sequence', d: 'M', f: 66.5, fn: 'longestConsecutive',
      plain: 'عددها مرتب نیستند. طولانی‌ترین رشته‌ی پشت‌سرهم مثل 1، 2، 3، 4 را پیدا کن. باید <b>O(n)</b> باشد، پس مرتب کردن ممنوع.',
      hint: 'همه را در یک set بریز. کدام عددها <i>شروع</i> یک رشته‌اند؟',
      idea: '<code>x</code> فقط وقتی شروع رشته است که <code>x − 1</code> در set نباشد. از هر شروع به بالا بشمار. هر عدد حداکثر دو بار دیده می‌شود، پس O(n) است.',
      traps: ['روی <b>set</b> حلقه بزن، نه روی لیست. با تکراری‌های زیاد، نسخه‌ی لیست ممکن است کند شود (TLE).', 'بدون بررسیِ «شروع است؟» الگوریتم O(n²) می‌شود.'],
      code: String.raw`class Solution:
    def longestConsecutive(self, nums):
        s = set(nums)
        best = 0
        for x in s:
            if x - 1 not in s:          # x starts a run
                y = x
                while y + 1 in s:
                    y += 1
                best = max(best, y - x + 1)
        return best`,
      O: 'O(n) time · O(n) space',
      tests: [[[[100, 4, 200, 1, 3, 2]], 4], [[[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], 9], [[[]], 0]]
    }
  ]
});
