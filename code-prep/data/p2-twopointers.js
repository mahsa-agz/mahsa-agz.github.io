pattern({
  id: 'twopointers', n: 2, name: 'Two pointers', sub: 'Each step throws away a whole row of options',
  why: `<p>Brute force on pairs checks every <code>(i, j)</code>: <b>n²</b>. Two pointers win because, when the data is <b>sorted</b> (or has two ends), one comparison rules out many pairs at once.</p>
<p>Example: sorted array, want sum = target. If <code>a[l] + a[r]</code> is <b>too small</b>, then <code>a[l]</code> with <i>any</i> element left of <code>r</code> is also too small, so <code>l</code> is useless and you move it. One step removes a whole row. That is why it is <b>O(n)</b>.</p>
<p>Two shapes:</p>
<ul><li><b>Opposite ends</b> (<code>l</code> → ← <code>r</code>): pairs in sorted data, palindromes, “container” problems.</li>
<li><b>Same direction</b> (writer <code>w</code> + reader): rewrite an array <b>in place</b>, keep only what you want.</li></ul>`,
  viz: `<div class="viz"><div class="vrow">${A([1, 3, 4, 6, 9], { 0: 'l', 4: 'r' })}</div><div class="vnote">target 10: 1 + 9 = 10 ✓ · if it were 12: 10 &lt; 12 → too small → <b>l</b> moves right</div></div>`,
  spot: ['array is <b>sorted</b> (or you may sort it)', '“pair / triplet with sum …”', '“palindrome”', '“in place”, “O(1) extra space”, “remove / move elements”', 'merge two sorted lists'],
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
  tiktok: `<b>3Sum</b>, <b>Trapping Rain Water</b> and <b>Container With Most Water</b> are all on TikTok's frequently asked list. CodeSignal Q1–Q2 often need the writer/reader shape on strings.`,
  problems: [
    {
      id: 'valid-palindrome', t: 'Valid Palindrome', d: 'E', f: 34.5, fn: 'isPalindrome',
      plain: 'After dropping everything except letters and digits, and ignoring case, does the text read the same both ways?',
      hint: 'Two pointers from both ends. What do you do when a pointer sits on a comma?',
      idea: 'Move <code>l</code> right past non-alphanumerics, <code>r</code> left the same way, then compare lowercase characters.',
      traps: ['<code>str.isalnum()</code> keeps digits too; the problem wants that.', 'Empty or all-symbol strings are palindromes (return True).'],
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
      plain: 'Move all 0s to the end, keep the order of the other numbers, change the list <b>in place</b>.',
      hint: 'A reader walks every item; a writer only moves when it gets a non-zero.',
      idea: 'Writer <code>w</code> marks where the next non-zero goes. Swap <code>a[w], a[i]</code> on every non-zero. Zeros drift to the end by themselves.',
      traps: ['Don\'t build a new list: the test checks the <b>same</b> list object.', 'Swapping (not copying) means no second loop to fill zeros.'],
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
      plain: 'Can the string become a palindrome if you delete <b>at most one</b> character?',
      hint: 'Walk inward until the first mismatch. You have one deletion: which two choices are there?',
      idea: 'At the first mismatch, try skipping the left char <b>or</b> the right char, and check if the rest is a plain palindrome.',
      traps: ['Only one deletion: after the mismatch use a simple check, not the same function again.', '<code>t == t[::-1]</code> is a fine way to check the rest.'],
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
      plain: 'Sorted array; find two numbers that add to <code>target</code>. Return positions <b>starting from 1</b>, using O(1) extra space.',
      hint: 'Sorted + pair sum: start at both ends. Which end moves when the sum is too big?',
      idea: 'Too small → <code>l += 1</code> (need bigger). Too big → <code>r -= 1</code>. Equal → done.',
      traps: ['Answer is 1-indexed: return <code>[l + 1, r + 1]</code>.', 'A hash map works too, but breaks the O(1) space rule.'],
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
      plain: 'Find all <b>different</b> triplets that sum to 0.',
      hint: 'Sort. Fix the first number; now the rest is Two Sum II. How do you avoid the same triplet twice?',
      idea: 'Sort. For each <code>i</code>, run opposite-end pointers on the part to its right looking for <code>-nums[i]</code>. Skip equal neighbours for <code>i</code>, and after a hit skip equal neighbours for <code>l</code>.',
      traps: ['Duplicates are the whole difficulty: skip <code>nums[i] == nums[i-1]</code>.', 'Small speed-up: if <code>nums[i] &gt; 0</code>, stop, since everything after is positive.'],
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
      plain: 'Lines of heights <code>h</code>. Pick two; water = <b>shorter height × distance</b>. Find the most water.',
      hint: 'Start with the widest pair. Moving the <i>taller</i> line inward: can that ever help?',
      idea: 'Width only shrinks as you move in, and the water is capped by the shorter line. So keeping the shorter line can never beat now → <b>move the shorter one</b>.',
      traps: ['The “why” is what interviewers ask: moving the taller side cannot raise the cap.', 'Area uses <code>r − l</code>, not <code>r − l + 1</code>.'],
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
