mix({
  id: 'mix1', after: 3, name: 'ترکیبی ۱', sub: 'الگوهای ۱ تا ۳ قاطی. اول الگو را حدس بزن، بعد حل کن.',
  problems: [
    {
      id: 'roman-to-integer', t: 'Roman to Integer', d: 'E', f: 34.5, fn: 'romanToInt', p: 'hashmap',
      tell: 'هسته‌اش یک <b>جدولِ جست‌وجو</b> (نماد ← مقدار) است. نشانه: «هر چیز را به یک مقدار نگاشت کن».',
      plain: 'عدد رومی مثل <code>"MCMXCIV"</code> را به عدد معمولی تبدیل کن.',
      hint: 'مقدارِ هر نماد را در دیکشنری بگذار. یک نماد کِی <i>کم</i> می‌شود؟',
      idea: 'از چپ به راست بخوان. اگر نمادی از نمادِ بعدی‌اش کوچک‌تر است (I قبل از V)، کمش کن؛ وگرنه اضافه‌اش کن.',
      traps: ['با نمادِ <b>بعدی</b> مقایسه کن و مراقب اندیسِ آخر باش.'],
      code: String.raw`class Solution:
    def romanToInt(self, s):
        v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        for i, c in enumerate(s):
            if i + 1 < len(s) and v[c] < v[s[i + 1]]:
                total -= v[c]
            else:
                total += v[c]
        return total`,
      O: 'O(n) time',
      tests: [[['III'], 3], [['LVIII'], 58], [['MCMXCIV'], 1994]]
    },
    {
      id: 'merge-sorted-array', t: 'Merge Sorted Array', d: 'E', f: 26.1, fn: 'merge', inplace: 0, p: 'twopointers',
      tell: '<b>دو لیستِ مرتب</b> + <b>در جا</b> ← دو اشاره‌گر. نکته‌ی خاص: از <b>آخر</b> پر کن.',
      plain: '<code>nums1</code>، <code>m</code> عدد و <code>n</code> جای خالی در انتها دارد. <code>nums2</code>ِ مرتب را در جا در آن ادغام کن.',
      hint: 'پر کردن از جلو عددهایی را که هنوز لازم داری پاک می‌کند. جای خالی کجاست؟',
      idea: 'اشاره‌گرها روی آخرین عددِ واقعیِ هر دو لیست، نویسنده روی آخرین خانه. بزرگ‌تر را در جای نویسنده بگذار و به چپ برو.',
      traps: ['اگر <code>nums1</code> زودتر تمام شود، بقیه‌ی <code>nums2</code> هنوز باید کپی شود (حلقه تا وقتی <code>j ≥ 0</code> ادامه دارد).'],
      code: String.raw`class Solution:
    def merge(self, nums1, m, nums2, n):
        i, j, w = m - 1, n - 1, m + n - 1
        while j >= 0:
            if i >= 0 and nums1[i] > nums2[j]:
                nums1[w] = nums1[i]; i -= 1
            else:
                nums1[w] = nums2[j]; j -= 1
            w -= 1`,
      O: 'O(m + n) time · O(1) space',
      tests: [[[[1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3], [1, 2, 2, 3, 5, 6]], [[[0], 0, [1], 1], [1]]]
    },
    {
      id: 'sort-colors', t: 'Sort Colors', d: 'M', f: 45.5, fn: 'sortColors', inplace: 0, p: 'twopointers',
      tell: '<b>در جا</b>، یک دور، فقط ۳ نوع مقدار ← اشاره‌گرهایی که مرز ناحیه‌ها را نشان می‌دهند.',
      plain: 'لیستی از 0، 1 و 2. آن را <b>در جا و در یک دور</b> مرتب کن، بدون <code>sort()</code>.',
      hint: 'سه ناحیه نگه دار: 0ها در چپ، 2ها در راست، ناشناخته‌ها در وسط.',
      idea: '<code>lo</code> = جای 0ِ بعدی، <code>hi</code> = جای 2ِ بعدی، <code>i</code> می‌خواند. 0 ← با <code>lo</code> جابه‌جا کن و هر دو را جلو ببر. 2 ← با <code>hi</code> جابه‌جا کن و فقط <code>hi</code> را حرکت بده (عددی که آمده هنوز بررسی نشده). 1 ← فقط <code>i</code> جلو برود.',
      traps: ['بعد از جابه‌جایی با <code>hi</code>، <code>i</code> را جلو <b>نبر</b>.', 'حلقه تا وقتی <code>i &lt;= hi</code> است.'],
      code: String.raw`class Solution:
    def sortColors(self, nums):
        lo, i, hi = 0, 0, len(nums) - 1
        while i <= hi:
            if nums[i] == 0:
                nums[lo], nums[i] = nums[i], nums[lo]
                lo += 1; i += 1
            elif nums[i] == 2:
                nums[hi], nums[i] = nums[i], nums[hi]
                hi -= 1
            else:
                i += 1`,
      O: 'O(n) time · O(1) space',
      tests: [[[[2, 0, 2, 1, 1, 0]], [0, 0, 1, 1, 2, 2]], [[[2, 0, 1]], [0, 1, 2]]]
    },
    {
      id: 'most-popular-video-creator', t: 'Most Popular Video Creator', d: 'M', f: 55.8, fn: 'mostPopularCreator', cmp: 'groups', p: 'hashmap',
      tell: '«مجموع برای هر سازنده»، «بهترین برای هر سازنده» ← <b>گروه‌بندی با دیکشنری</b>. (یک سؤالِ کاملاً تیک‌تاکی.)',
      plain: 'هر ویدیو یک سازنده، یک شناسه (id) و تعداد بازدید دارد. سازنده‌هایی را پیدا کن که <b>بیشترین مجموع بازدید</b> را دارند؛ برای هر کدام، شناسه‌ی پربازدیدترین ویدیواش را بده (در تساوی ← شناسه‌ای که از نظر الفبایی کوچک‌تر است).',
      hint: 'دو دیکشنری: مجموع بازدیدِ هر سازنده، و بهترین (بازدید، شناسه) برای هر سازنده.',
      idea: 'یک دور: بازدید را به <code>total[c]</code> اضافه کن؛ بهترین ویدیوی هر سازنده را با مقایسه‌ی <code>(−views, id)</code> نگه دار، پس کوچک‌تر یعنی بهتر. بعد سازنده‌هایی را که مجموعشان بیشینه است انتخاب کن.',
      traps: ['در تساویِ بازدید، شناسه‌ی <b>کوچک‌تر</b> (الفبایی) برنده است.', 'چند سازنده می‌توانند با هم اول باشند؛ همه را برگردان.'],
      code: String.raw`class Solution:
    def mostPopularCreator(self, creators, ids, views):
        total, best = {}, {}
        for c, i, v in zip(creators, ids, views):
            total[c] = total.get(c, 0) + v
            if c not in best or (-v, i) < best[c]:
                best[c] = (-v, i)
        top = max(total.values())
        return [[c, best[c][1]] for c in total if total[c] == top]`,
      O: 'O(n) time',
      tests: [[[['alice', 'bob', 'alice', 'chris'], ['one', 'two', 'three', 'four'], [5, 10, 5, 4]], [['alice', 'one'], ['bob', 'two']]], [[['alice', 'alice', 'alice'], ['a', 'b', 'c'], [1, 2, 2]], [['alice', 'b']]]]
    },
    {
      id: 'maximum-points-you-can-obtain-from-cards', t: 'Maximum Points You Can Obtain from Cards', d: 'M', f: 34.5, fn: 'maxScore', p: 'window',
      tell: 'برداشتن از <b>دو سر</b> یک <b>وسطِ پیوسته</b> با اندازه‌ی ثابت باقی می‌گذارد ← برعکسش کن و پنجره‌ی لغزانِ ثابت بگیر.',
      plain: 'دقیقاً <code>k</code> کارت بردار، هر بار از سرِ چپ یا راست. بیشترین امتیاز؟',
      hint: 'بعد از برداشتنِ <code>k</code> کارت از دو سر، چه چیزی روی میز می‌ماند؟',
      idea: 'کارت‌هایی که می‌مانند یک تکه‌ی پیوسته به اندازه‌ی <code>n − k</code> هستند. بیشترین برداشت = مجموع کل − <b>کمترین</b> جمعِ یک پنجره به اندازه‌ی <code>n − k</code>.',
      traps: ['وقتی <code>k == n</code> اندازه‌ی پنجره 0 است: جواب مجموع کل است.'],
      code: String.raw`class Solution:
    def maxScore(self, cardPoints, k):
        n, w = len(cardPoints), len(cardPoints) - k
        cur = sum(cardPoints[:w])
        low = cur
        for r in range(w, n):
            cur += cardPoints[r] - cardPoints[r - w]
            low = min(low, cur)
        return sum(cardPoints) - low`,
      O: 'O(n) time · O(1) space',
      tests: [[[[1, 2, 3, 4, 5, 6, 1], 3], 12], [[[2, 2, 2], 2], 4], [[[9, 7, 7, 9, 7, 7, 9], 7], 55]]
    },
    {
      id: 'count-complete-subarrays-in-an-array', t: 'Count Complete Subarrays in an Array', d: 'M', f: 55.8, fn: 'countCompleteSubarrays', p: 'window',
      tell: '«<b>زیرآرایه‌هایی</b> را بشمار که همه‌ی … را دارند» ← پنجره با <code>Counter</code>؛ وقتی یکی معتبر شد، همه‌ی بلندترهایش هم معتبرند.',
      plain: 'زیرآرایه‌ای «کامل» است که به اندازه‌ی کل آرایه مقدارِ متفاوت داشته باشد. آن‌ها را بشمار.',
      hint: 'اگر <code>[l, r]</code> کامل است، <code>[l, r+1]</code>، <code>[l, r+2]</code>، … هم کامل‌اند. چند تا می‌شوند؟',
      idea: '<code>D</code> = تعداد مقدارهای متفاوت. <code>r</code> را بزرگ کن. تا وقتی پنجره <code>D</code> مقدارِ متفاوت دارد، هر <code>n − r</code> ادامه‌اش کامل است: اضافه‌شان کن، بعد از <code>l</code> کوچک کن.',
      traps: ['ترفند شمارش: <code>n − r</code> اضافه کن، نه 1.', 'کلیدهای 0 را حذف کن تا <code>len(cnt)</code> درست بماند.'],
      code: String.raw`from collections import Counter

class Solution:
    def countCompleteSubarrays(self, nums):
        D, n = len(set(nums)), len(nums)
        cnt, l, ans = Counter(), 0, 0
        for r, x in enumerate(nums):
            cnt[x] += 1
            while len(cnt) == D:
                ans += n - r
                cnt[nums[l]] -= 1
                if cnt[nums[l]] == 0: del cnt[nums[l]]
                l += 1
        return ans`,
      O: 'O(n) time',
      tests: [[[[1, 3, 1, 2, 2]], 4], [[[5, 5, 5, 5]], 10]]
    },
    {
      id: 'trapping-rain-water', t: 'Trapping Rain Water', d: 'H', f: 79.1, fn: 'trap', p: 'twopointers',
      tell: 'هر خانه به بلندترین ستونِ چپش <b>و</b> راستش بستگی دارد ← از <b>دو سر</b> به داخل بیا.',
      plain: 'ستون‌هایی با ارتفاع <code>h</code>. چقدر آب باران بینشان می‌ماند؟',
      hint: 'آبِ بالای خانه‌ی i = کمینه‌ی (بلندترینِ چپ، بلندترینِ راست) − h[i]. درباره‌ی کدام سمت به‌اندازه‌ی کافی می‌دانی؟',
      idea: 'اشاره‌گر در دو سر، با <code>lmax</code> و <code>rmax</code>. اگر <code>lmax &lt; rmax</code>، خانه‌ی چپ قطعاً با <code>lmax</code> محدود می‌شود (سمت راست حداقل همین‌قدر بلند است): <code>lmax − h[l]</code> را اضافه کن و <code>l</code> را جلو ببر. وگرنه همین کار را از راست بکن.',
      traps: ['بیشینه را <b>قبل</b> از اضافه کردنِ آب به‌روز کن تا آب منفی نشود.', 'نسخه‌ای با آرایه‌های بیشینه‌ی پیشوندی/پسوندی O(n) حافظه می‌گیرد و قبول است؛ قدم اولِ خوبی است.'],
      code: String.raw`class Solution:
    def trap(self, height):
        l, r = 0, len(height) - 1
        lmax = rmax = water = 0
        while l < r:
            lmax = max(lmax, height[l])
            rmax = max(rmax, height[r])
            if lmax < rmax:
                water += lmax - height[l]; l += 1
            else:
                water += rmax - height[r]; r -= 1
        return water`,
      O: 'O(n) time · O(1) space',
      tests: [[[[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], 6], [[[4, 2, 0, 3, 2, 5]], 9]]
    }
  ]
});
