pattern({
  id: 'twopointers', n: 2, name: 'دو اشاره‌گر (Two pointers)', sub: 'هر قدم یک ردیف کامل از حالت‌ها را حذف می‌کند',
  story: `<p>این الگو یک مخترعِ مشخص ندارد؛ از <b>ادغام</b> آمده. <b>سال ۱۹۴۵، جان فون نویمان (John von Neumann)</b> مرتب‌سازیِ ادغامی (merge sort) را نوشت. قلبش این است: دو دسته کارتِ مرتب داری، یک انگشت روی بالای هر دسته؛ کوچک‌تر را بردار و فقط همان انگشت را جلو ببر. دو انگشت = دو اشاره‌گر. هیچ‌وقت لازم نیست به عقب نگاه کنی، چون مرتب بودن تضمین می‌کند چیزی جا نمانده.</p>
<p>بعدها <b>ادسخر دایکسترا (Edsger Dijkstra)</b> مسئله‌ی <b>«پرچم هلند»</b> را مطرح کرد: توپ‌های قرمز، سفید و آبی را در یک دور و در جا مرتب کن. جوابش سه اشاره‌گر است که مرز ناحیه‌ها را نگه می‌دارند (همان سؤال Sort Colors در ترکیبی ۱). <b>شهود اصلی:</b> وقتی داده نظم دارد، هر مقایسه به تو می‌گوید کدام طرف دیگر به درد نمی‌خورد.</p>`,
  uses: `<ul>
<li><b>ادغام دو داده‌ی مرتب</b>: دو لاگِ مرتب‌شده بر اساس زمان را یکی کن. پانداس <code>merge_asof</code> همین کار را می‌کند.</li>
<li><b>جفت با جمعِ مشخص در داده‌ی مرتب</b> (و سه‌تایی با یک حلقه‌ی اضافه).</li>
<li><b>مقایسه‌ی دو سر</b>: پالیندروم، برعکس کردن در جا.</li>
<li><b>فیلتر یا جداسازی در جا</b> بدون حافظه‌ی اضافه: حذف تکراری‌ها، صفرها به آخر، جدا کردنِ کوچک/بزرگ (قلبِ quicksort).</li>
<li><b>جاهایی که خوب نیست:</b> داده‌ی <b>نامرتب</b> که نباید مرتبش کنی (چون اندیس‌ها مهم‌اند) ← هش‌مپ.</li></ul>`,
  demo: {
    title: 'جفت با جمع target در آرایه‌ی مرتب',
    fields: [['nums (sorted)', '1, 3, 4, 6, 8, 11'], ['target', '10']],
    run(f) {
      const a = nums(f['nums (sorted)']).sort((x, y) => x - y), t = +f.target, out = [], gone = new Set();
      let l = 0, r = a.length - 1;
      out.push({ cells: A(a, { [l]: 'l', [r]: 'r' }), note: `از دو سر شروع کن. هدف ${t}.` });
      while (l < r) {
        const s = a[l] + a[r];
        if (s === t) { out.push({ cells: A(a, { [l]: 'l ✓', [r]: 'r ✓' }, null, gone), note: `${L(`${a[l]} + ${a[r]} = ${s}`)} ✓ پیدا شد.` }); return out; }
        if (s < t) { gone.add(l); out.push({ cells: A(a, { [l + 1]: 'l', [r]: 'r' }, null, gone), note: `${L(`${a[l]} + ${a[r]} = ${s} &lt; ${t}`)} ← کوچک است. ${a[l]} حتی با بزرگ‌ترین عددِ باقی‌مانده هم کم می‌آورد، پس با <b>هیچ</b> عددی جواب نمی‌دهد ← حذفش کن، <b>l</b> جلو.` }); l++; }
        else { gone.add(r); out.push({ cells: A(a, { [l]: 'l', [r - 1]: 'r' }, null, gone), note: `${L(`${a[l]} + ${a[r]} = ${s} &gt; ${t}`)} ← بزرگ است. ${a[r]} حتی با کوچک‌ترین عددِ باقی‌مانده هم زیاد است ← حذفش کن، <b>r</b> عقب.` }); r--; }
      }
      out.push({ cells: A(a, {}, null, gone), note: 'اشاره‌گرها به هم رسیدند: جفتی وجود ندارد.' });
      return out;
    }
  },
  why: `<p>راه‌حل ساده برای جفت‌ها همه‌ی <code>(i, j)</code>ها را امتحان می‌کند: <b>n²</b>. دو اشاره‌گر برنده است چون وقتی داده <b>مرتب</b> است (یا دو سر دارد)، یک مقایسه هم‌زمان کلی جفت را کنار می‌گذارد.</p>
<p>مثال: آرایه‌ی مرتب، دنبال جمعِ برابر با target. اگر <code>a[l] + a[r]</code> <b>کوچک‌تر</b> باشد، <code>a[l]</code> با <i>هر</i> عضوِ سمت چپِ <code>r</code> هم کوچک‌تر است؛ پس <code>l</code> به درد نمی‌خورد و جلو می‌رود. یک قدم، یک ردیف کامل حذف. برای همین <b>O(n)</b> است.</p>
<p>دو شکل دارد:</p>
<ul><li><b>از دو سر</b> (<code>l</code> → ← <code>r</code>): جفت در داده‌ی مرتب، پالیندروم، سؤال‌های «ظرف آب».</li>
<li><b>هم‌جهت</b> (نویسنده <code>w</code> + خواننده): بازنویسی آرایه <b>در جا (in place)</b> و نگه داشتن فقط چیزهایی که می‌خواهی.</li></ul>`,
  viz: `<div class="viz"><div class="vrow">${A([1, 3, 4, 6, 9], { 0: 'l', 4: 'r' })}</div><div class="vnote"><span dir="ltr">target = 10: 1 + 9 = 10</span> ✓ · اگر <span dir="ltr">target = 12</span> بود: <span dir="ltr">10 &lt; 12</span> ← کوچک است ← <b>l</b> یک خانه جلو می‌رود</div></div>`,
  spot: ['آرایه <b>مرتب</b> است (یا اجازه داری مرتبش کنی)', '«جفت / سه‌تایی با جمعِ …»', '«پالیندروم» (palindrome)', '«در جا»، «حافظه‌ی اضافه‌ی O(1)»، «حذف / جابه‌جا کردن عضوها»', 'ادغام دو لیست مرتب'],
  template: String.raw`# opposite ends
l, r = 0, len(a) - 1
while l < r:
    s = a[l] + a[r]
    if s == target: return [l, r]
    if s < target: l += 1          # need bigger
    else:          r -= 1          # need smaller

# same direction: writer + reader
w = 0
for x in a:                        # reader
    if keep(x):
        a[w] = x                   # writer
        w += 1`,
  tiktok: `<b>3Sum</b>، <b>Trapping Rain Water</b> و <b>Container With Most Water</b> همه در فهرست سؤال‌های پرتکرار تیک‌تاک هستند. سؤال ۱ و ۲ کدسیگنال روی رشته‌ها اغلب شکلِ نویسنده/خواننده را لازم دارند.`,
  problems: [
    {
      id: 'valid-palindrome', t: 'Valid Palindrome', d: 'E', f: 34.5, fn: 'isPalindrome',
      plain: 'اگر همه‌چیز جز حروف و رقم‌ها را دور بریزی و بزرگی و کوچکیِ حروف را نادیده بگیری، متن از دو طرف یکی خوانده می‌شود؟',
      hint: 'دو اشاره‌گر از دو سر. وقتی اشاره‌گر روی ویرگول است چه می‌کنی؟',
      idea: '<code>l</code> را از روی کاراکترهای غیرحرف‌ورقم به راست رد کن، <code>r</code> را به چپ، بعد حروف کوچک‌شده را مقایسه کن.',
      traps: ['<code>str.isalnum()</code> رقم‌ها را هم نگه می‌دارد؛ سؤال همین را می‌خواهد.', 'رشته‌ی خالی یا فقط‌علامت پالیندروم است (True).'],
      code: String.raw`class Solution:
    def isPalindrome(self, s):
        l, r = 0, len(s) - 1
        while l < r:
            if not s[l].isalnum(): l += 1
            elif not s[r].isalnum(): r -= 1
            elif s[l].lower() != s[r].lower(): return False
            else:
                l += 1; r -= 1
        return True`,
      O: 'O(n) time · O(1) space',
      tests: [[['A man, a plan, a canal: Panama'], true], [['race a car'], false], [[' '], true]]
    },
    {
      id: 'move-zeroes', t: 'Move Zeroes', d: 'E', f: 26.1, fn: 'moveZeroes', inplace: 0,
      plain: 'همه‌ی صفرها را به آخر ببر، ترتیب بقیه‌ی عددها را حفظ کن، و همان لیست را <b>در جا</b> تغییر بده.',
      hint: 'خواننده از روی همه رد می‌شود؛ نویسنده فقط وقتی عدد غیرصفر می‌بیند حرکت می‌کند.',
      idea: 'نویسنده‌ی <code>w</code> جای عدد غیرصفرِ بعدی را نشان می‌دهد. روی هر غیرصفر، <code>a[w], a[i]</code> را جابه‌جا کن. صفرها خودبه‌خود به آخر می‌روند.',
      traps: ['لیست جدید نساز: تست <b>همان</b> لیست را بررسی می‌کند.', 'با جابه‌جا کردن (نه کپی) دیگر حلقه‌ی دوم برای پر کردن صفرها لازم نیست.'],
      code: String.raw`class Solution:
    def moveZeroes(self, nums):
        w = 0
        for i in range(len(nums)):
            if nums[i] != 0:
                nums[w], nums[i] = nums[i], nums[w]
                w += 1`,
      O: 'O(n) time · O(1) space',
      tests: [[[[0, 1, 0, 3, 12]], [1, 3, 12, 0, 0]], [[[0]], [0]]]
    },
    {
      id: 'valid-palindrome-ii', t: 'Valid Palindrome II', d: 'E', f: 34.5, fn: 'validPalindrome',
      plain: 'اگر <b>حداکثر یک</b> حرف را پاک کنی، رشته می‌تواند پالیندروم شود؟',
      hint: 'تا اولین ناجوری جلو برو. یک بار حق حذف داری: دو انتخاب چیست؟',
      idea: 'در اولین ناجوری، یا حرف چپ را کنار بگذار <b>یا</b> حرف راست را، و ببین بقیه یک پالیندروم ساده است یا نه.',
      traps: ['فقط یک حذف: بعد از ناجوری یک بررسیِ ساده بکن، نه صدا زدن دوباره‌ی همین تابع.', '<code>t == t[::-1]</code> راه خوبی برای بررسی بقیه است.'],
      code: String.raw`class Solution:
    def validPalindrome(self, s):
        l, r = 0, len(s) - 1
        while l < r:
            if s[l] != s[r]:
                a, b = s[l+1:r+1], s[l:r]      # skip left / skip right
                return a == a[::-1] or b == b[::-1]
            l += 1; r -= 1
        return True`,
      O: 'O(n) time',
      tests: [[['aba'], true], [['abca'], true], [['abc'], false]]
    },
    {
      id: 'two-sum-ii-input-array-is-sorted', t: 'Two Sum II – Input Array Is Sorted', d: 'M', f: 26.1, fn: 'twoSum',
      plain: 'آرایه مرتب است؛ دو عدد پیدا کن که جمعشان <code>target</code> شود. جایگاه‌ها را <b>از 1</b> برگردان، با حافظه‌ی اضافه‌ی O(1).',
      hint: 'مرتب + جمع جفت: از دو سر شروع کن. وقتی جمع بزرگ است کدام سر حرکت می‌کند؟',
      idea: 'کوچک ← <code>l += 1</code> (عدد بزرگ‌تر لازم است). بزرگ ← <code>r -= 1</code>. برابر ← تمام.',
      traps: ['جواب از 1 شروع می‌شود: <code>[l + 1, r + 1]</code> را برگردان.', 'هش‌مپ هم کار می‌کند، ولی قانونِ حافظه‌ی O(1) را می‌شکند.'],
      code: String.raw`class Solution:
    def twoSum(self, numbers, target):
        l, r = 0, len(numbers) - 1
        while l < r:
            s = numbers[l] + numbers[r]
            if s == target: return [l + 1, r + 1]
            if s < target: l += 1
            else: r -= 1`,
      O: 'O(n) time · O(1) space',
      tests: [[[[2, 7, 11, 15], 9], [1, 2]], [[[2, 3, 4], 6], [1, 3]], [[[-1, 0], -1], [1, 2]]]
    },
    {
      id: '3sum', t: '3Sum', d: 'M', f: 68.2, fn: 'threeSum', cmp: 'groups',
      plain: 'همه‌ی سه‌تایی‌های <b>متفاوت</b> را پیدا کن که جمعشان 0 شود.',
      hint: 'مرتب کن. عدد اول را ثابت بگیر؛ حالا بقیه همان Two Sum II است. چطور از سه‌تاییِ تکراری جلوگیری می‌کنی؟',
      idea: 'مرتب کن. برای هر <code>i</code>، روی بخشِ سمت راستش با دو اشاره‌گر دنبال <code>-nums[i]</code> بگرد. همسایه‌های برابرِ <code>i</code> را رد کن، و بعد از هر پیدا کردن، همسایه‌های برابرِ <code>l</code> را هم.',
      traps: ['کل سختیِ سؤال تکراری‌هاست: <code>nums[i] == nums[i-1]</code> را رد کن.', 'سرعت بیشتر: اگر <code>nums[i] &gt; 0</code> شد، متوقف شو؛ بعدی‌ها همه مثبت‌اند.'],
      code: String.raw`class Solution:
    def threeSum(self, nums):
        nums.sort()
        out = []
        for i in range(len(nums) - 2):
            if nums[i] > 0: break
            if i and nums[i] == nums[i - 1]: continue
            l, r = i + 1, len(nums) - 1
            while l < r:
                s = nums[i] + nums[l] + nums[r]
                if s < 0: l += 1
                elif s > 0: r -= 1
                else:
                    out.append([nums[i], nums[l], nums[r]])
                    l += 1; r -= 1
                    while l < r and nums[l] == nums[l - 1]: l += 1
        return out`,
      O: 'O(n²) time · O(1) extra',
      tests: [[[[-1, 0, 1, 2, -1, -4]], [[-1, -1, 2], [-1, 0, 1]]], [[[0, 0, 0, 0]], [[0, 0, 0]]], [[[0, 1, 1]], []]]
    },
    {
      id: 'container-with-most-water', t: 'Container With Most Water', d: 'M', f: 55.8, fn: 'maxArea',
      plain: 'خط‌هایی با ارتفاع <code>h</code>. دو تا را انتخاب کن؛ آب = <b>ارتفاعِ کوتاه‌تر × فاصله</b>. بیشترین آب را پیدا کن.',
      hint: 'از پهن‌ترین جفت شروع کن. حرکت دادنِ خطِ <i>بلندتر</i> به داخل هیچ‌وقت کمک می‌کند؟',
      idea: 'با رفتن به داخل، پهنا فقط کم می‌شود و آب را خطِ کوتاه‌تر محدود می‌کند. پس نگه داشتنِ خط کوتاه‌تر هیچ‌وقت از الان بهتر نمی‌شود ← <b>خطِ کوتاه‌تر را حرکت بده</b>.',
      traps: ['مصاحبه‌گر همین «چرا» را می‌پرسد: حرکتِ سمتِ بلندتر سقف را بالا نمی‌برد.', 'مساحت با <code>r − l</code> حساب می‌شود، نه <code>r − l + 1</code>.'],
      code: String.raw`class Solution:
    def maxArea(self, height):
        l, r, best = 0, len(height) - 1, 0
        while l < r:
            best = max(best, min(height[l], height[r]) * (r - l))
            if height[l] < height[r]: l += 1
            else: r -= 1
        return best`,
      O: 'O(n) time · O(1) space',
      tests: [[[[1, 8, 6, 2, 5, 4, 8, 3, 7]], 49], [[[1, 1]], 1]]
    }
  ]
});
