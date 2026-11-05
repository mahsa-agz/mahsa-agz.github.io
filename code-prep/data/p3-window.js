pattern({
  id: 'window', n: 3, name: 'Sliding window', sub: 'Grow the right side, shrink the left, never go back',
  why: `<p>A substring or subarray is a <b>window</b> <code>[l, r]</code>. Checking every window is <b>n²</b> (or worse).</p>
<p>The key fact: for these problems, <b>if a window is bad, any bigger window that contains it is also bad</b> (too many repeats, too many distinct values, …). So when the window goes bad, you only need to move <code>l</code> forward; it never has to come back.</p>
<p>Each index enters once (when <code>r</code> reaches it) and leaves once (when <code>l</code> passes it): <b>O(n)</b>. Keep a small <b>state</b> (a sum or a <code>Counter</code>) and update it as items enter and leave, instead of recomputing.</p>
<p class="note">Needs that “bad stays bad” rule. Sums with <b>negative</b> numbers break it, so those go to <i>Prefix sums</i> (pattern 4).</p>`,
  viz: `<div class="viz"><div class="vrow">${A(['a', 'b', 'c', 'a', 'b', 'b'], { 1: 'l', 3: 'r' }, [1, 3])}</div><div class="vnote">window “bca” has no repeats → length 3 · next char “b” is a repeat → move <b>l</b> past the old “b”</div></div>`,
  spot: ['“<b>longest / shortest</b> substring / subarray such that …”', '“at most k …”, “contains all of …”', '<b>contiguous</b> (must be next to each other)', '“every window of size k”'],
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
  tiktok: `<b>Longest Substring Without Repeating Characters</b> is one of TikTok's 6 most asked. Its premium cousin <b>“at most K distinct characters”</b> was asked in the last 3 months. <b>Fruit Into Baskets</b> below is the free version of the same idea.`,
  problems: [
    {
      id: 'best-time-to-buy-and-sell-stock', t: 'Best Time to Buy and Sell Stock', d: 'E', f: 62.8, fn: 'maxProfit',
      plain: 'Buy one day, sell on a <b>later</b> day. Biggest profit, or 0.',
      hint: 'If you sell today, which buy day is best? Can you know it without looking back?',
      idea: 'Keep the cheapest price so far (the left edge). Selling today earns <code>price − cheapest</code>. Track the max.',
      traps: ['Selling before buying is not allowed, which is why you update the minimum as you go, not upfront.'],
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
      plain: 'Length of the longest piece of the string with <b>no repeated character</b>.',
      hint: 'When <code>s[r]</code> repeats, where must the new left edge be?',
      idea: 'Remember the last index of each char. If <code>s[r]</code> was seen inside the window, jump <code>l</code> to one past it.',
      traps: ['Use <code>l = max(l, last[c] + 1)</code>; an old index left of the window must not pull <code>l</code> back (“abba”).'],
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
      plain: 'All numbers are positive. Shortest piece with sum <b>≥ target</b>. Return 0 if none.',
      hint: 'This is the “shortest valid” shape: while it is valid, try to shrink.',
      idea: 'Add <code>a[r]</code>. While <code>total ≥ target</code>: record the length, then remove <code>a[l]</code> and move <code>l</code>.',
      traps: ['Return 0 when nothing works (best is still ∞).', 'Works only because all numbers are positive.'],
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
      plain: 'Longest piece of the list that has <b>at most 2 different values</b>.',
      hint: 'State = a <code>Counter</code> of the window. When is it invalid?',
      idea: 'Add <code>fruits[r]</code> to the counter. While it has more than 2 keys, drop <code>fruits[l]</code> (delete the key when its count hits 0).',
      traps: ['Delete keys at 0, otherwise <code>len(cnt)</code> stays too big.', 'Change 2 to k and you have the TikTok premium problem “at most K distinct”.'],
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
      plain: 'You may flip at most <code>k</code> zeros to ones. Longest run of ones?',
      hint: 'Rephrase: longest window with <b>at most k zeros</b>.',
      idea: 'Count zeros in the window. While zeros &gt; k, move <code>l</code> (subtract if <code>a[l]</code> was 0).',
      traps: ['You don\'t actually flip anything; you just count zeros.'],
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
      plain: 'Start positions in <code>s</code> where a rearrangement of <code>p</code> appears.',
      hint: 'Window size is fixed: <code>len(p)</code>. What do you compare?',
      idea: 'Fixed window. Keep letter counts of the window; add <code>s[r]</code>, remove <code>s[r − m]</code>; when counts equal <code>p</code>\'s, record <code>r − m + 1</code>.',
      traps: ['Comparing two 26-length lists is O(26) = constant, fine.', 'Guard <code>len(p) &gt; len(s)</code> (just returns []).'],
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
      plain: 'Shortest piece of <code>s</code> that contains <b>every letter of <code>t</code></b> (with repeats). Return it, or "".',
      hint: 'Shortest-valid shape. Instead of comparing counters each step, keep one number: how many letters are still <i>missing</i>.',
      idea: '<code>need</code> = counts of t, <code>missing = len(t)</code>. Add <code>s[r]</code>: if it was still needed, <code>missing −= 1</code>. While <code>missing == 0</code>: record, then give back <code>s[l]</code> (if that makes it needed again, <code>missing += 1</code>).',
      traps: ['<code>need</code> may go negative for extra letters; that is fine and correct.', 'Return the string, not the length.'],
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
