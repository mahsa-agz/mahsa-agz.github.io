pattern({
  id: 'hashmap', n: 1, name: 'Hash map', sub: 'Remember what you have seen',
  why: `<p>A list answers “is <code>x</code> here?” by checking every item: <b>O(n)</b>. A hash map (<code>dict</code> / <code>set</code>) turns the key into an address with a hash function, so it jumps straight to the right slot: <b>O(1)</b> on average.</p>
<p>So the trade is simple: <b>spend memory to stop searching</b>. Any time your brute force has an inner loop that <i>looks for something</i>, ask: “could I have written it down earlier?”</p>
<p>Three ways to use it:</p>
<ul><li><b>Lookup</b>: store what you've seen, then ask “is my partner already here?”</li>
<li><b>Count</b>: <code>Counter</code> gives frequencies in one pass.</li>
<li><b>Group</b>: the key is a <i>signature</i> that equal things share (sorted letters, remainder, …).</li></ul>`,
  viz: `<div class="viz"><div class="vrow">${A([2, 7, 11, 15], { 1: 'x' })}</div><div class="vnote">at <b>7</b>: need 9 − 7 = <b>2</b> → is 2 in <code>seen</code>? <b>yes</b> (index 0) → answer [0, 1]</div><div class="vrow"><span class="kv">seen = { 2: 0 }</span></div></div>`,
  spot: ['“find two items that add up / match”', '“how many times / most frequent”', '“group things that are the same in some way”', '“duplicate / unique / first non-repeating”', 'your brute force is two nested loops and the inner one just <i>searches</i>'],
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
  tiktok: `Hash maps hide inside many of TikTok's top questions. <b>LRU Cache</b>, TikTok's most asked problem, is a hash map plus a linked list; it comes later in “Design”. In CodeSignal tests, Q1–Q2 are often a single <code>Counter</code> away from solved.`,
  problems: [
    {
      id: 'two-sum', t: 'Two Sum', d: 'E', f: 66.5, fn: 'twoSum',
      plain: 'Find the <b>positions</b> of two different numbers that add up to <code>target</code>. Exactly one answer exists.',
      hint: 'For each number <code>x</code>, which number would complete it? Where could you have stored it?',
      idea: 'Walk once. For each <code>x</code>, the partner is <code>target − x</code>. If it is already in <code>seen</code>, done. Otherwise store <code>x → index</code>.',
      traps: ['Check <b>before</b> storing, so you never pair a number with itself (<code>[3,3], 6</code> still works because the first 3 is stored first).', 'Sorting breaks the original indexes.'],
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
      plain: 'Put words made of <b>the same letters</b> into the same group (“eat”, “tea”, “ate”).',
      hint: 'What is identical for all anagrams of a word, and could it be a dictionary key?',
      idea: 'The signature is the sorted word: <code>"eat" → "aet"</code>. Use it as the key and append each word to its group.',
      traps: ['Lists cannot be dict keys. Use a string (<code>"".join(sorted(w))</code>) or a tuple.', 'Faster key for long words: a tuple of 26 letter counts, O(k) instead of O(k log k).'],
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
      plain: 'Return the <code>k</code> values that appear <b>most often</b>. Any order is fine.',
      hint: 'Count first. Then: a count can never be bigger than <code>n</code>. Could the count itself be an index?',
      idea: 'Count with <code>Counter</code>. Make buckets where <code>bucket[c]</code> holds values seen <code>c</code> times. Read buckets from high to low until you have <code>k</code>.',
      traps: ['Sorting all counts is O(n log n); fine in a test, but say the bucket idea in an interview.', 'Quick valid alternative: <code>[v for v, _ in Counter(nums).most_common(k)]</code>.'],
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
      plain: 'Count pairs of songs <code>i &lt; j</code> whose total length is a multiple of 60.',
      hint: 'Only the remainder <code>t % 60</code> matters. Which remainder completes remainder <code>r</code>?',
      idea: 'It is Two Sum on remainders, but you <b>count</b> instead of returning. Partner of <code>r</code> is <code>(60 − r) % 60</code>. Add how many partners you have seen, then record <code>r</code>.',
      traps: ['<code>(60 − r) % 60</code> makes remainder 0 pair with 0 (not 60).', 'Count first, then record, so a song never pairs with itself.'],
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
      plain: 'Numbers are unsorted. Find the longest run like 1, 2, 3, 4. Must be <b>O(n)</b>, so no sorting.',
      hint: 'Put everything in a set. Which numbers are the <i>start</i> of a run?',
      idea: '<code>x</code> starts a run only if <code>x − 1</code> is not in the set. From each start, count upward. Every number is touched at most twice, so it is O(n).',
      traps: ['Loop over the <b>set</b>, not the list. With many duplicates the list version can time out.', 'Without the “is a start?” check it becomes O(n²).'],
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
