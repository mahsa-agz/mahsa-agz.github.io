mix({
  id: 'mix1', after: 3, name: 'Mixed 1', sub: 'Patterns 1–3, shuffled. First guess the pattern, then solve.',
  problems: [
    {
      id: 'roman-to-integer', t: 'Roman to Integer', d: 'E', f: 34.5, fn: 'romanToInt', p: 'hashmap',
      tell: 'A fixed <b>lookup table</b> (symbol → value) is the core. Recognize: “map each thing to a value”.',
      plain: 'Turn a Roman numeral like <code>"MCMXCIV"</code> into a number.',
      hint: 'Store each symbol\'s value in a dict. When does a symbol <i>subtract</i>?',
      idea: 'Read left to right. If a symbol is smaller than the one after it (I before V), subtract it; otherwise add it.',
      traps: ['Compare with the <b>next</b> symbol; guard the last index.'],
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
      tell: '<b>Two sorted lists</b> + <b>in place</b> → two pointers. The twist: fill from the <b>back</b>.',
      plain: '<code>nums1</code> has <code>m</code> numbers plus <code>n</code> empty slots at the end. Merge sorted <code>nums2</code> into it, in place.',
      hint: 'Filling from the front overwrites numbers you still need. Where is free space?',
      idea: 'Pointers at the last real numbers of both lists, writer at the very end. Put the bigger one at the writer, move left.',
      traps: ['When <code>nums1</code> runs out first, the rest of <code>nums2</code> must still be copied (the loop runs while <code>j ≥ 0</code>).'],
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
      tell: '<b>In place</b>, one pass, only 3 kinds of value → pointers that mark zones.',
      plain: 'A list of 0s, 1s and 2s. Sort it <b>in place, in one pass</b>, without <code>sort()</code>.',
      hint: 'Keep three zones: 0s on the left, 2s on the right, unknown in the middle.',
      idea: '<code>lo</code> = next spot for 0, <code>hi</code> = next spot for 2, <code>i</code> reads. 0 → swap to <code>lo</code>, move both. 2 → swap to <code>hi</code>, move <code>hi</code> only (the swapped-in value is not checked yet). 1 → just move <code>i</code>.',
      traps: ['After swapping with <code>hi</code>, do <b>not</b> move <code>i</code>.', 'Loop while <code>i &lt;= hi</code>.'],
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
      tell: '“Total per creator”, “best per creator” → <b>group-by with a dict</b>. (A very TikTok-style question.)',
      plain: 'Each video has a creator, an id and views. Find the creators with the <b>most total views</b>; for each, give their most-viewed video id (tie → smallest id alphabetically).',
      hint: 'Two dicts: total views per creator, and best (views, id) per creator.',
      idea: 'One pass: add views to <code>total[c]</code>; keep the best video per creator by comparing <code>(−views, id)</code>, so smaller means better. Then pick creators with the max total.',
      traps: ['Tie on views → the lexicographically <b>smaller</b> id wins.', 'Several creators can tie for the top; return all.'],
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
      tell: 'Taking from both <b>ends</b> leaves a <b>contiguous middle</b> of fixed size → flip it into a fixed sliding window.',
      plain: 'Take exactly <code>k</code> cards, each from the left or right end. Max total points?',
      hint: 'What is left on the table after you take <code>k</code> cards from the ends?',
      idea: 'The cards you leave are one contiguous block of size <code>n − k</code>. Max taken = total − <b>min</b> sum of a window of size <code>n − k</code>.',
      traps: ['When <code>k == n</code> the window size is 0: answer is the total.'],
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
      tell: '“Count <b>subarrays</b> that contain all …” → window with a <code>Counter</code>; once valid, every longer one is valid too.',
      plain: 'A subarray is “complete” if it has as many different values as the whole array. Count them.',
      hint: 'If <code>[l, r]</code> is complete, then <code>[l, r+1]</code>, <code>[l, r+2]</code>, … are too. How many is that?',
      idea: 'Let <code>D</code> = number of distinct values. Grow <code>r</code>. While the window has <code>D</code> distinct values, all <code>n − r</code> extensions are complete: add them, then shrink from <code>l</code>.',
      traps: ['Counting trick: add <code>n − r</code>, not 1.', 'Delete keys at 0 so <code>len(cnt)</code> is correct.'],
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
      tell: 'Each spot depends on the tallest bar to its left <b>and</b> right → walk in from <b>both ends</b>.',
      plain: 'Bars of heights <code>h</code>. How much rain stays trapped between them?',
      hint: 'Water above spot i = min(tallest on left, tallest on right) − h[i]. Which side do you already know enough about?',
      idea: 'Pointers at both ends with <code>lmax</code>, <code>rmax</code>. If <code>lmax &lt; rmax</code>, the left spot is limited by <code>lmax</code> for sure (the right side is at least that tall): add <code>lmax − h[l]</code>, move <code>l</code>. Else do the same on the right.',
      traps: ['Update the max <b>before</b> adding water, so it is never negative.', 'A prefix-max/suffix-max array version is O(n) space and also accepted; good first step.'],
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
