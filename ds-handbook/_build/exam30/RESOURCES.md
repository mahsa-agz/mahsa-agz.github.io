# Exam resources: Data Scientist at TikTok/ByteDance, Samsung, Google (Meta and Amazon as references)

Checked on 2026-10-07. Every URL below returned HTTP 200 to a scripted GET request unless the line is marked:
- **(browser)**: the site blocks scripted checks (LeetCode answers 403 through Cloudflare). The URL format is standard, the pages were confirmed through LeetCode's public GraphQL API or a web search, and they open normally in a browser.
- **(login)** / **(Premium)**: free pages exist, but this feature needs an account or a paid plan.

Dead or wrong URLs found during checking were dropped: HI company pages for Samsung and ByteDance (404), DataLemur's ByteDance SQL blog and Google DS guide (404), and Baekjoon (see the Samsung section).

---

## 1. HI (free pages)

HI's coding and ML-system-design guides are free to read. Login only adds progress tracking. Premium adds interactive visualizations, "Guided Practice", and the full recent-question feed. There is no dedicated data-science track; the ML System Design guide is the closest match.

### Coding patterns / DSA (https://www.hellointerview.com/learn/code)
| Page | Good for |
|---|---|
| https://www.hellointerview.com/learn/code | Index of all pattern chapters. Use it as the 30-day DSA checklist |
| https://www.hellointerview.com/learn/code/two-pointers/overview | Why sorted input lets you go from O(n^2) to O(n); 3Sum, container, trapping rain water |
| https://www.hellointerview.com/learn/code/sliding-window/fixed-length | Fixed-size window template (max sum of size k) |
| https://www.hellointerview.com/learn/code/sliding-window/variable-length | Grow/shrink window template (longest substring without repeats) |
| https://www.hellointerview.com/learn/code/intervals/overview | Sort-by-start template; merge / insert / meeting rooms |
| https://www.hellointerview.com/learn/code/stack/overview | Stack basics; valid parentheses, decode string |
| https://www.hellointerview.com/learn/code/stack/monotonic-stack | Monotonic stack (daily temperatures, largest rectangle) |
| https://www.hellointerview.com/learn/code/linked-list/overview | Fast/slow pointers, reversal, dummy head |
| https://www.hellointerview.com/learn/code/binary-search/overview | Binary search, including "binary search on the answer" |
| https://www.hellointerview.com/learn/code/heap/overview | Top-k, k-way merge, streaming median |
| https://www.hellointerview.com/learn/code/depth-first-search/introduction | Tree DFS: return values versus global variables |
| https://www.hellointerview.com/learn/code/depth-first-search/matrices | Grid DFS (flood fill, islands). Core for Samsung-style grid problems |
| https://www.hellointerview.com/learn/code/breadth-first-search/introduction | BFS level order, shortest path in unweighted graphs |
| https://www.hellointerview.com/learn/code/breadth-first-search/rotting-oranges | Multi-source BFS on a grid. Classic Samsung/TikTok shape |
| https://www.hellointerview.com/learn/code/backtracking/overview | Subsets / permutations / N-Queens template |
| https://www.hellointerview.com/learn/code/graphs/topological-sort | Kahn's algorithm (course schedule) |
| https://www.hellointerview.com/learn/code/graphs/shortest-path-algorithms | Dijkstra / Bellman-Ford with worked problems |
| https://www.hellointerview.com/learn/code/dynamic-programming/fundamentals | How to define state and transitions; 1-D and 2-D DP |
| https://www.hellointerview.com/learn/code/greedy/overview | When greedy works (stock, jump game, gas station) |
| https://www.hellointerview.com/learn/code/trie/overview | Prefix trees |
| https://www.hellointerview.com/learn/code/prefix-sum/overview | Prefix sums plus a hash map (subarray sum equals k) |
| https://www.hellointerview.com/learn/code/matrices/spiral-matrix | Matrix simulation (spiral / rotate). Samsung-style index handling |

### ML system design (free "in a hurry" guide)
| Page | Good for |
|---|---|
| https://www.hellointerview.com/learn/ml-system-design/in-a-hurry/introduction | What MLSD exams test and how they are scored |
| https://www.hellointerview.com/learn/ml-system-design/in-a-hurry/delivery | Step-by-step answer framework (problem, data, features, model, eval, serving) |
| https://www.hellointerview.com/learn/ml-system-design/core-concepts/feature-engineering | Feature types, encoding, leakage |
| https://www.hellointerview.com/learn/ml-system-design/core-concepts/embeddings | Two-tower models and embedding retrieval |
| https://www.hellointerview.com/learn/ml-system-design/core-concepts/generalization | Overfitting, regularisation, distribution shift |
| https://www.hellointerview.com/learn/ml-system-design/core-concepts/evaluation | Offline metrics versus online A/B evaluation. The DS bridge topic |
| https://www.hellointerview.com/learn/ml-system-design/problem-breakdowns/video-recommendations | Worked example of a TikTok For-You-style recommender |
| https://www.hellointerview.com/learn/ml-system-design/problem-breakdowns/harmful-content | Worked example: content-moderation classifier |
| https://www.hellointerview.com/learn/ml-system-design/problem-breakdowns/bot-detection | Worked example: fraud/bot detection (imbalanced labels) |

### Community-reported questions
| Page | Good for |
|---|---|
| https://www.hellointerview.com/community/questions/company/TikTok | User-reported TikTok questions (filter by level and type; the full feed is partly Premium) |
| https://www.hellointerview.com/community/questions/company/Google | Same for Google |
| https://www.hellointerview.com/community/questions/company/Meta | Same for Meta |
| https://www.hellointerview.com/community/questions/company/Amazon | Same for Amazon |
| https://www.hellointerview.com/learn/behavioral | Free behavioral-exam course (STAR stories, levelling) |

---

## 2. LeetCode and curated lists

### Company tags (browser, Premium for frequency and full lists)
- https://leetcode.com/company/tiktok/
- https://leetcode.com/company/bytedance/
- https://leetcode.com/company/samsung/
- https://leetcode.com/company/google/
- https://leetcode.com/company/facebook/ (the Meta tag uses the historical `facebook` slug)
- https://leetcode.com/company/amazon/

Without Premium you only see a partial list with no frequency. The free GitHub mirrors below export the same data, including frequency.

### Public study plans and lists
| List | URL | Notes |
|---|---|---|
| Top Exam 150 | https://leetcode.com/studyplan/top-interview-150/ (browser) | Free. Confirmed through the GraphQL API (`studyPlanV2Detail`) |
| LeetCode 75 | https://leetcode.com/studyplan/leetcode-75/ (browser) | Free. A good 2 to 3 week core set |
| SQL 50 | https://leetcode.com/studyplan/top-sql-50/ (browser) | Free. Do it alongside DataLemur |
| 30 Days of Pandas | https://leetcode.com/studyplan/30-days-of-pandas/ (browser) | Free. Pandas versions of SQL questions, useful for DS take-homes |
| Introduction to Pandas | https://leetcode.com/studyplan/introduction-to-pandas/ (browser) | Free warm-up |
| Grind 75 | https://www.techinterviewhandbook.org/grind75/ | Free. Choose weeks and hours per week, and it builds a schedule |
| TIH: best practice questions | https://www.techinterviewhandbook.org/best-practice-questions/ | Free. Origin and explanation of Blind 75 / Grind 75 |
| TIH: coding cheatsheet | https://www.techinterviewhandbook.org/coding-interview-cheatsheet/ | Free. Before/during/after-exam checklist |
| NeetCode practice (NeetCode 150) | https://neetcode.io/practice | Free list and videos. Some courses are paid |
| NeetCode roadmap | https://neetcode.io/roadmap | Free. Pattern dependency graph (arrays, then two pointers, and so on) |
| Blind 75 (NeetCode version) | https://neetcode.io/practice/practice/blind75 | Free, with video solutions |
| Blind 75 (original post) | https://www.teamblind.com/post/New-Year-Gift---Curated-List-of-Top-75-LeetCode-Questions-to-Save-Your-Time-OaM1orEU | The original 2018 list |
| AlgoMonster flowchart | https://algo.monster/flowchart | Free. "Which pattern?" decision tree |

### Company-wise problem repos (free, GitHub)
| Repo | Notes |
|---|---|
| https://github.com/liquidslr/leetcode-company-wise-problems | **Used for the table below.** About 31k stars, updated in Aug 2026. One folder per company (TikTok, ByteDance, Samsung, Google, Meta, Amazon...) with CSVs for 30 days / 3 months / 6 months / more than 6 months / All, and columns Difficulty, Title, Frequency, Acceptance, Link, Topics |
| https://github.com/snehasishroy/leetcode-companywise-interview-questions | Similar export, updated in Aug 2026 |
| https://github.com/krishnadey30/LeetCode-Questions-CompanyWise | Older (2024) but widely used. Includes problem IDs |
| https://github.com/hxu296/leetcode-company-wise-problems-2022 | 2022 snapshot |

### Exam-experience posts (browser, found via web search)
- https://leetcode.com/discuss/interview-question/4377581/Tiktok-VO-Full-Loop/ (TikTok full virtual onsite)
- https://leetcode.com/discuss/interview-question/2729466/TikTok-OA-questions-(Latest)/ (TikTok online assessment)
- https://leetcode.com/discuss/interview-experience/2761691/ (Samsung R&D Bangalore, SWE)

### Frequently asked problems: TikTok / ByteDance / Samsung / Google (+ Meta, Amazon)

**Source:** liquidslr/leetcode-company-wise-problems, `<Company>/5. All.csv` (and `3. Six Months.csv` for Google), downloaded on 2026-10-07. Problem numbers were mapped from the slugs with LeetCode's public `api/problems/all` endpoint. Titles, difficulty, and company membership come straight from those CSVs; the pattern column is my label.

**Selection:** the top 30 TikTok problems, the top 20 Google problems from the last 6 months, the top 12 Samsung, and the top 10 ByteDance, all by frequency. Two trivial or SQL items were dropped, and 17 high-frequency Google/Meta/Amazon staples were added.

**Companies column:** shows the rank by frequency in each company's All list. For Google, Meta, and Amazon, which have 1,400 to 2,300 tagged problems, a company appears only if the problem is in that company's top 150. TikTok, ByteDance, and Samsung are listed whenever the problem is tagged at all.

Small samples: Samsung has 62 tagged problems and ByteDance 63, so their rankings are noisy. Treat the Samsung rows as LeetCode-tagged problems, not as the Korean SW competency test (see section 3).

| # | Title | Difficulty | Pattern | Companies (rank by frequency in that company's "All" list) |
|---|---|---|---|---|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) | Easy | Hash map | TikTok #37; ByteDance #13; Samsung #26; Google #1; Meta #6; Amazon #1 |
| 2 | [Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | Medium | Linked list | TikTok #266; ByteDance #22; Google #2; Meta #36; Amazon #8 |
| 3 | [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Medium | Sliding window | TikTok #4; Google #7; Meta #48; Amazon #5 |
| 4 | [Median of Two Sorted Arrays](https://leetcode.com/problems/median-of-two-sorted-arrays/) | Hard | Binary search (partition) | TikTok #183; Samsung #56; Google #3; Meta #55; Amazon #12 |
| 5 | [Longest Palindromic Substring](https://leetcode.com/problems/longest-palindromic-substring/) | Medium | Expand around center / DP | TikTok #15; ByteDance #47; Samsung #57; Google #13; Meta #53; Amazon #9 |
| 7 | [Reverse Integer](https://leetcode.com/problems/reverse-integer/) | Medium | Math (overflow) | Google #19; Meta #100; Amazon #53 |
| 9 | [Palindrome Number](https://leetcode.com/problems/palindrome-number/) | Easy | Math | Google #6; Meta #61; Amazon #26 |
| 11 | [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | Medium | Two pointers | TikTok #74; Google #15; Meta #68; Amazon #13 |
| 14 | [Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) | Easy | String / trie | TikTok #107; Google #5; Meta #46; Amazon #20 |
| 15 | [3Sum](https://leetcode.com/problems/3sum/) | Medium | Two pointers | TikTok #18; Samsung #33; Google #8; Meta #44; Amazon #11 |
| 20 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) | Easy | Stack | TikTok #34; ByteDance #50; Samsung #42; Google #17; Meta #34; Amazon #17 |
| 21 | [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) | Easy | Linked list | TikTok #184; Google #27; Meta #85; Amazon #38 |
| 22 | [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) | Medium | Backtracking | TikTok #47; Samsung #38; Google #28; Meta #81; Amazon #31 |
| 23 | [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | Hard | Heap | TikTok #27; ByteDance #54; Samsung #36; Google #99; Meta #32; Amazon #18 |
| 26 | [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | Easy | Two pointers | Google #22; Meta #52; Amazon #46 |
| 30 | [Substring with Concatenation of All Words](https://leetcode.com/problems/substring-with-concatenation-of-all-words/) | Hard | Sliding window + hash map | Samsung #6 |
| 31 | [Next Permutation](https://leetcode.com/problems/next-permutation/) | Medium | Array (two pointers) | TikTok #127; Samsung #40; Google #29; Meta #26; Amazon #48 |
| 33 | [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) | Medium | Binary search | TikTok #16; ByteDance #17; Samsung #43; Google #38; Meta #84; Amazon #24 |
| 39 | [Combination Sum](https://leetcode.com/problems/combination-sum/) | Medium | Backtracking | TikTok #73; ByteDance #7; Google #112; Amazon #127 |
| 42 | [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | Hard | Two pointers / monotonic stack | TikTok #9; ByteDance #31; Samsung #8; Google #4; Meta #66; Amazon #3 |
| 49 | [Group Anagrams](https://leetcode.com/problems/group-anagrams/) | Medium | Hash map | TikTok #100; Google #55; Meta #82; Amazon #7 |
| 51 | [N-Queens](https://leetcode.com/problems/n-queens/) | Hard | Backtracking | TikTok #17; Google #43; Amazon #68 |
| 53 | [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | Medium | Kadane / DP | TikTok #122; ByteDance #27; Samsung #44; Google #25; Meta #76; Amazon #22 |
| 54 | [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/) | Medium | Matrix simulation | TikTok #21; Google #31; Meta #116; Amazon #41 |
| 56 | [Merge Intervals](https://leetcode.com/problems/merge-intervals/) | Medium | Intervals (sort) | TikTok #8; ByteDance #8; Samsung #45; Google #23; Meta #17; Amazon #14 |
| 68 | [Text Justification](https://leetcode.com/problems/text-justification/) | Hard | Simulation (string) | TikTok #11; ByteDance #55; Google #145 |
| 76 | [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | Hard | Sliding window | TikTok #13; Meta #41; Amazon #55 |
| 79 | [Word Search](https://leetcode.com/problems/word-search/) | Medium | Backtracking on grid | TikTok #14; Samsung #47; Amazon #42 |
| 88 | [Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) | Easy | Two pointers (from end) | TikTok #347; Samsung #52; Google #10; Meta #14; Amazon #25 |
| 121 | [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Easy | Greedy (running min) | TikTok #38; ByteDance #21; Samsung #34; Google #9; Meta #22; Amazon #6 |
| 128 | [Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | Medium | Hash set | TikTok #25; Google #11; Meta #94; Amazon #27 |
| 138 | [Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/) | Medium | Linked list + hash map | TikTok #304; Meta #29; Amazon #29 |
| 146 | [LRU Cache](https://leetcode.com/problems/lru-cache/) | Medium | Design (hash map + doubly linked list) | TikTok #1; ByteDance #1; Samsung #1; Google #40; Meta #27; Amazon #2 |
| 169 | [Majority Element](https://leetcode.com/problems/majority-element/) | Easy | Boyer-Moore voting | Google #16; Meta #87; Amazon #30 |
| 199 | [Binary Tree Right Side View](https://leetcode.com/problems/binary-tree-right-side-view/) | Medium | Tree BFS | TikTok #63; ByteDance #63; Meta #16; Amazon #90 |
| 200 | [Number of Islands](https://leetcode.com/problems/number-of-islands/) | Medium | Grid DFS/BFS | TikTok #2; ByteDance #5; Samsung #10; Google #24; Meta #58; Amazon #4 |
| 207 | [Course Schedule](https://leetcode.com/problems/course-schedule/) | Medium | Topological sort | TikTok #10; ByteDance #6; Google #84; Meta #57; Amazon #15 |
| 210 | [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) | Medium | Topological sort | TikTok #6; Amazon #39 |
| 215 | [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Medium | Heap / quickselect | TikTok #39; ByteDance #33; Google #61; Meta #5; Amazon #54 |
| 221 | [Maximal Square](https://leetcode.com/problems/maximal-square/) | Medium | Grid DP | TikTok #149; ByteDance #10; Google #87 |
| 227 | [Basic Calculator II](https://leetcode.com/problems/basic-calculator-ii/) | Medium | Stack | TikTok #36; ByteDance #9; Meta #7 |
| 236 | [Lowest Common Ancestor of a Binary Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | Medium | Tree DFS | TikTok #102; Meta #13; Amazon #28 |
| 253 | [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) | Medium | Intervals + heap | TikTok #7; Google #32; Meta #108; Amazon #56 |
| 300 | [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) | Medium | DP / binary search | TikTok #3; ByteDance #30; Samsung #2; Google #76; Amazon #125 |
| 312 | [Burst Balloons](https://leetcode.com/problems/burst-balloons/) | Hard | Interval DP | Samsung #3 |
| 316 | [Remove Duplicate Letters](https://leetcode.com/problems/remove-duplicate-letters/) | Medium | Monotonic stack + greedy | TikTok #84; ByteDance #2 |
| 322 | [Coin Change](https://leetcode.com/problems/coin-change/) | Medium | DP (unbounded knapsack) | TikTok #22; Google #108; Meta #132; Amazon #49 |
| 347 | [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | Medium | Heap / bucket sort | TikTok #23; ByteDance #14; Google #41; Meta #23; Amazon #23 |
| 374 | [Guess Number Higher or Lower](https://leetcode.com/problems/guess-number-higher-or-lower/) | Easy | Binary search | Samsung #7 |
| 394 | [Decode String](https://leetcode.com/problems/decode-string/) | Medium | Stack | TikTok #12; ByteDance #18; Google #36; Meta #115 |
| 528 | [Random Pick with Weight](https://leetcode.com/problems/random-pick-with-weight/) | Medium | Prefix sum + binary search | TikTok #92; Meta #10 |
| 543 | [Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) | Easy | Tree DFS | TikTok #246; Meta #12; Amazon #130 |
| 560 | [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | Medium | Prefix sum + hash map | TikTok #19; ByteDance #40; Google #21; Meta #11; Amazon #21 |
| 670 | [Maximum Swap](https://leetcode.com/problems/maximum-swap/) | Medium | Greedy | TikTok #26; Meta #43 |
| 680 | [Valid Palindrome II](https://leetcode.com/problems/valid-palindrome-ii/) | Easy | Two pointers | TikTok #219; Meta #3 |
| 694 | [Number of Distinct Islands](https://leetcode.com/problems/number-of-distinct-islands/) | Medium | Grid DFS + hashing shapes | TikTok #5 |
| 767 | [Reorganize String](https://leetcode.com/problems/reorganize-string/) | Medium | Greedy + heap | TikTok #135; Amazon #10 |
| 827 | [Making A Large Island](https://leetcode.com/problems/making-a-large-island/) | Hard | Grid DFS + union-find | TikTok #28; Meta #39 |
| 875 | [Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) | Medium | Binary search on answer | TikTok #93; Google #37; Meta #80; Amazon #16 |
| 987 | [Vertical Order Traversal of a Binary Tree](https://leetcode.com/problems/vertical-order-traversal-of-a-binary-tree/) | Hard | Tree BFS/DFS + sorting | Samsung #9; Meta #47 |
| 994 | [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) | Medium | Multi-source BFS | TikTok #79; ByteDance #19; Samsung #30; Google #82; Amazon #19 |
| 1081 | [Smallest Subsequence of Distinct Characters](https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/) | Medium | Monotonic stack + greedy | ByteDance #3 |
| 1091 | [Shortest Path in Binary Matrix](https://leetcode.com/problems/shortest-path-in-binary-matrix/) | Medium | Grid BFS | TikTok #182; Meta #24 |
| 1146 | [Snapshot Array](https://leetcode.com/problems/snapshot-array/) | Medium | Design + binary search | TikTok #30 |
| 1151 | [Minimum Swaps to Group All 1's Together](https://leetcode.com/problems/minimum-swaps-to-group-all-1s-together/) | Medium | Sliding window (fixed) | TikTok #20 |
| 1249 | [Minimum Remove to Make Valid Parentheses](https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/) | Medium | Stack | TikTok #112; Meta #1 |
| 1301 | [Number of Paths with Max Score](https://leetcode.com/problems/number-of-paths-with-max-score/) | Hard | Grid DP | Samsung #11 |
| 1405 | [Longest Happy String](https://leetcode.com/problems/longest-happy-string/) | Medium | Greedy + heap | TikTok #29 |
| 1997 | [First Day Where You Have Been in All the Rooms](https://leetcode.com/problems/first-day-where-you-have-been-in-all-the-rooms/) | Medium | DP | ByteDance #4 |
| 2334 | [Subarray With Elements Greater Than Varying Threshold](https://leetcode.com/problems/subarray-with-elements-greater-than-varying-threshold/) | Hard | Monotonic stack | TikTok #24 |
| 2662 | [Minimum Cost of a Path With Special Roads](https://leetcode.com/problems/minimum-cost-of-a-path-with-special-roads/) | Medium | Dijkstra | Samsung #12 |
| 3045 | [Count Prefix and Suffix Pairs II](https://leetcode.com/problems/count-prefix-and-suffix-pairs-ii/) | Hard | Trie / string hashing | Samsung #4 |
| 3080 | [Mark Elements on Array by Performing Queries](https://leetcode.com/problems/mark-elements-on-array-by-performing-queries/) | Medium | Heap + simulation | Samsung #5 |

Suggested priority if time is short: the problems tagged by 4 or more companies (LRU Cache, Number of Islands, LIS, Merge Intervals, Trapping Rain Water, Course Schedule, Longest Palindromic Substring, Search in Rotated Sorted Array, Subarray Sum Equals K, Top K Frequent, Merge k Sorted Lists, Two Sum, Best Time to Buy and Sell Stock, Valid Parentheses, 3Sum, Coin Change, Spiral Matrix, Longest Substring Without Repeating Characters).

---

## 3. Samsung specifics

**Format.** Samsung's careers site describes the SW Competency Test as coding on a PC: 2 problems in 240 minutes, in C, C++, Java or Python. Practice is through SW Expert Academy. The test is **implementation-heavy**:
- grid simulation (robots, snakes, dice, marbles, sharks)
- BFS/DFS on 2-D boards
- brute force with backtracking
- rotating or shifting 2-D arrays

The difficulty comes from getting many rules exactly right, not from advanced algorithms. Python may be restricted (for example, no `sys` in some environments). Check which test your track uses: DS/AI roles at Samsung Research or SDS may instead use a GSAT plus a separate coding round. Samsung R&D India uses a 3-question online test, then a 3-hour "advanced" test.

| Resource | URL | Notes |
|---|---|---|
| Samsung Careers: recruiting process | https://www.samsungcareers.com/guide/process?lang=en | Official description of the SW Competency Test (2 problems, 240 min, C/C++/Java/Python) and GSAT |
| SW Expert Academy (SWEA) | https://swexpertacademy.com/main/main.do | Samsung's official practice site. Free with an account (login needed to submit) |
| SWEA problem list | https://swexpertacademy.com/main/code/problem/problemList.do | Filter by difficulty (D1 to D8). The "모의 SW 역량테스트" (mock test) set is the closest to the real exam |
| CodeTree | https://www.codetree.ai/ | Korean platform that hosts recreations of recent Samsung SW test problems (search "삼성 SW 역량테스트 기출"). Partly paid |
| Solutions repo (C++ and Python) | https://github.com/bloodstrawberry/Samsung_Software_Competency_Test_A_Type | Answer code for CodeTree versions of A-type past problems. Shows the expected simulation style |
| LeetCode Samsung tag | https://leetcode.com/company/samsung/ (browser, Premium) | Used mainly by Samsung R&D India / SRA. Its 62 problems lean to DP and graph |

**About Baekjoon.** Baekjoon Online Judge (acmicpc.net) is the usual home of the past-problem list ("삼성 SW 역량 테스트 기출 문제"). It shut down on 2026-04-28 and was later acquired by Day1Company. All acmicpc.net URLs returned 404 during this check, so none are linked. The classic past-problem names are still worth searching for on CodeTree or blogs: 구슬 탈출 2, 2048 (Easy), 뱀, 주사위 굴리기, 테트로미노, 연구소, 로봇 청소기, 톱니바퀴, 감시, 치킨 배달, 아기 상어, 미세먼지 안녕!

**LeetCode analogues for the same skills:**
- Number of Islands (200), Rotting Oranges (994), Shortest Path in Binary Matrix (1091): grid BFS
- Spiral Matrix (54), Rotate Image (48): index simulation
- Word Search (79), N-Queens (51): backtracking
- Making A Large Island (827), Number of Distinct Islands (694)

---

## 4. SQL practice

| Resource | URL | Free? | Notes |
|---|---|---|---|
| DataLemur question bank | https://datalemur.com/questions | Mostly free; some questions and solutions are Premium | Real FAANG-style SQL. Filter by company in the UI (TikTok, Google, Meta, Amazon...) |
| DataLemur TikTok SQL questions | https://datalemur.com/blog/tiktok-sql-interview-questions | Free | TikTok-tagged SQL questions with solutions |
| DataLemur Google SQL questions | https://datalemur.com/blog/google-sql-interview-questions | Free | Google |
| DataLemur Samsung SQL questions | https://datalemur.com/blog/samsung-sql-interview-questions | Free | Samsung |
| DataLemur Meta SQL questions | https://datalemur.com/blog/facebook-sql-interview-questions | Free | Meta reference |
| DataLemur Amazon SQL questions | https://datalemur.com/blog/amazon-sql-interview-questions | Free | Amazon reference |
| DataLemur SQL tutorial | https://datalemur.com/sql-tutorial | Free | Interactive tutorial up to window functions |
| LeetCode SQL 50 | https://leetcode.com/studyplan/top-sql-50/ (browser) | Free | 50 graded problems |
| StrataScratch | https://www.stratascratch.com/ and https://platform.stratascratch.com/coding | Free tier (a subset of questions and solutions); full access is paid; login needed to run code | Large bank tagged by company, with both SQL and pandas |
| Mode / ThoughtSpot SQL tutorial | https://mode.com/sql-tutorial/ (now redirects to https://www.thoughtspot.com/sql-tutorial) | Free | Classic beginner-to-advanced tutorial. Window functions: https://www.thoughtspot.com/sql-tutorial/sql-window-functions |
| SQLBolt | https://sqlbolt.com/ | Free | Quick interactive basics |
| SQL Practice | https://www.sql-practice.com/ | Free | In-browser hospital DB exercises |
| SQLite window functions | https://www.sqlite.org/windowfunctions.html | Free | Reference for practicing on the local `chinook.sqlite` / `northwind.db` |
| PostgreSQL window functions | https://www.postgresql.org/docs/current/functions-window.html | Free | Reference |

---

## 5. Statistics, A/B testing, product sense

| Resource | URL | Notes |
|---|---|---|
| Trustworthy Online Controlled Experiments (Kohavi, Tang, Xu) | https://experimentguide.com/ | The book's site, with chapter list and resources. The book itself is paid; it is *the* A/B-testing reference used at Google, Microsoft and LinkedIn |
| ExP Platform (Kohavi et al.) | https://exp-platform.com/ | Free papers and talks: pitfalls, SRM, Twyman's law, metrics |
| Microsoft ExP research group | https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/ | Free articles. For example, during-experiment checks (SRM and others): https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-during-experiment-stage/ |
| Evan Miller's A/B tools | https://www.evanmiller.org/ab-testing/ | Sample-size calculator: https://www.evanmiller.org/ab-testing/sample-size.html ; chi-squared: https://www.evanmiller.org/ab-testing/chi-squared.html ; t-test: https://www.evanmiller.org/ab-testing/t-test.html |
| "How Not To Run an A/B Test" | https://www.evanmiller.org/how-not-to-run-an-ab-test.html | Peeking problem. A very common exam question |
| Simple sequential A/B testing | https://www.evanmiller.org/sequential-ab-testing.html | Follow-up answer to "how can you stop early?" |
| Udacity A/B Testing (Google) | https://www.udacity.com/course/ab-testing--ud257 | Free course by Google data scientists. Metric choice, sanity checks, sizing |
| Seeing Theory (Brown) | https://seeing-theory.brown.edu/ | Visual probability, distributions, CLT, inference, regression |
| StatQuest | https://statquest.org/video-index/ and https://www.youtube.com/@statquest | Short, clear videos on stats and ML (p-values, power, regression, trees) |
| OpenIntro Statistics | https://www.openintro.org/book/os/ | Free textbook (PDF). Inference, proportions, regression |
| Think Stats 3e | https://greenteapress.com/wp/think-stats-3e/ | Free; stats in Python/pandas |
| DataLemur: 50 A/B testing questions | https://datalemur.com/blog/ab-testing-interview-questions-and-answers | Free. Duration, pitfalls, randomisation, novelty, network effects |
| DataLemur: statistics questions | https://datalemur.com/blog/statistics-interview-questions-data-science | Free |
| DataLemur: product-sense questions | https://datalemur.com/blog/product-sense-interview-questions | Free. Metric definition, metric drops, trade-offs |
| DataLemur: TikTok DS exam guide | https://datalemur.com/blog/tiktok-data-scientist-interview-guide | Free. Process and 22 reported questions |
| DataLemur: Meta DS exam guide | https://datalemur.com/blog/meta-data-scientist-interview-guide | Free. Analytical-execution and analytical-reasoning rounds (the reference template for product DS) |
| Ace the DS book | https://www.acethedatascienceinterview.com/ | Book site (the book is paid). The authors run DataLemur, which is the free companion |
| IQ: company guides | https://www.interviewquery.com/guides/tiktok-data-scientist , https://www.interviewquery.com/guides/bytedance-data-scientist , https://www.interviewquery.com/guides/google-data-scientist , https://www.interviewquery.com/guides/samsung-data-scientist , https://www.interviewquery.com/guides/meta-data-scientist , https://www.interviewquery.com/guides/amazon-data-scientist | Free overviews of process and rounds; many question answers are paid |
| IQ: A/B answer framework | https://www.interviewquery.com/p/how-to-answer-ab-testing-interview-questions | Free 6-step template |
| IQ: product DS questions | https://www.interviewquery.com/p/product-data-science-interview | Free. Product and metric case questions |
| IQ: top DS questions | https://www.interviewquery.com/p/data-science-interview-questions | Free. Broad question list |
| alexeygrigorev/data-science-exams | https://github.com/alexeygrigorev/data-science-interviews | Free theory Q&A (stats, ML) |

---

## 6. ML / Deep learning / LLMs

| Resource | URL | Notes |
|---|---|---|
| Chip Huyen: Chip Huyen's ML book | https://huyenchip.com/ml-interviews-book/ | Free. Exam process plus about 200 knowledge questions. Math chapter: https://huyenchip.com/ml-interviews-book/contents/chapter-5.-math.html |
| Chip Huyen: Building LLM applications for production | https://huyenchip.com/2023/04/11/llm-engineering.html | Prompting versus fine-tuning, evaluation, cost and latency |
| Google ML Crash Course | https://developers.google.com/machine-learning/crash-course | Free. Regression, classification metrics (https://developers.google.com/machine-learning/crash-course/classification), embeddings, LLM intro |
| Google: Rules of ML | https://developers.google.com/machine-learning/guides/rules-of-ml | 43 practical rules. Great for MLSD answers |
| Google: Recommendation systems course | https://developers.google.com/machine-learning/recommendation | Candidate generation, scoring, re-ranking (TikTok-relevant) |
| Hugging Face LLM course | https://huggingface.co/learn/llm-course/chapter1/1 | Free. Transformers, tokenizers, fine-tuning. All courses: https://huggingface.co/learn |
| Jay Alammar: Illustrated Transformer | https://jalammar.github.io/illustrated-transformer/ | The standard visual explanation of attention |
| Jay Alammar: Illustrated GPT-2 / BERT / word2vec | https://jalammar.github.io/illustrated-gpt2/ , https://jalammar.github.io/illustrated-bert/ , https://jalammar.github.io/illustrated-word2vec/ | Decoder-only models, pretraining/fine-tuning, embeddings |
| Andrej Karpathy: Neural Networks Zero to Hero | https://karpathy.ai/zero-to-hero.html | Free video course: micrograd, makemore, GPT |
| Karpathy videos | https://www.youtube.com/@AndrejKarpathy | Key ones: "Let's build GPT" https://www.youtube.com/watch?v=kCc8FmEb1nY ; "Intro to LLMs" https://www.youtube.com/watch?v=zjkBMFhNj_g ; "Deep Dive into LLMs like ChatGPT" https://www.youtube.com/watch?v=7xTGNNLPyMI ; backprop/micrograd https://www.youtube.com/watch?v=VMj-3S1tku0 ; "Let's reproduce GPT-2" https://www.youtube.com/watch?v=l8pRSuU81PU |
| Lilian Weng: Lil'Log | https://lilianweng.github.io/ | Deep surveys. Attention: https://lilianweng.github.io/posts/2018-06-24-attention/ ; Transformer family v2: https://lilianweng.github.io/posts/2023-01-27-the-transformer-family-v2/ ; LLM agents: https://lilianweng.github.io/posts/2023-06-23-agent/ ; large-model training: https://lilianweng.github.io/posts/2021-09-25-train-large/ ; reward hacking: https://lilianweng.github.io/posts/2024-11-28-reward-hacking/ |
| Stanford CS229 | https://cs229.stanford.edu/ ; main notes PDF https://cs229.stanford.edu/main_notes.pdf | Classic ML math (GLMs, SVM, EM, bias-variance) |
| Stanford CME 295: Transformers and LLMs | https://cme295.stanford.edu/ | Compact LLM course (by the authors of the "VIP cheatsheets") |
| Stanford CS336: LM from scratch | https://stanford-cs336.github.io/ (redirects to cs336.stanford.edu) | Deep LLM internals, if time allows |
| An Introduction to Statistical Learning (ISLP) | https://www.statlearning.com/ | Free PDF. The best single classic-ML / statistics textbook for DS |
| Elements of Statistical Learning | https://hastie.su.domains/ElemStatLearn/ | Free PDF. Advanced reference |
| Deep Learning Book (Goodfellow et al.) | https://www.deeplearningbook.org/ | Free online |
| Dive into Deep Learning | https://d2l.ai/ | Free, with runnable code (PyTorch) |
| scikit-learn user guide | https://scikit-learn.org/stable/user_guide.html ; metrics https://scikit-learn.org/stable/modules/model_evaluation.html | API and concept reference |
| 3Blue1Brown: neural networks | https://www.3blue1brown.com/topics/neural-networks | Visual intuition for backprop and transformers |
| ML system design repos | https://github.com/khangich/machine-learning-interview , https://github.com/alirezadir/Machine-Learning-Interviews (now redirects to `alirezadir/AIMLInterviews`) | Free MLSD and ML-coding question collections |
| youssefHosni DS Q&A | https://github.com/youssefHosni/Data-Science-Interview-Questions-Answers | Free stats, ML and DL Q&A |

---

## 7. Cheat-sheet references

| Topic | URL |
|---|---|
| Python `collections` (Counter, deque, defaultdict) | https://docs.python.org/3/library/collections.html |
| Python `heapq` | https://docs.python.org/3/library/heapq.html |
| Python `bisect` | https://docs.python.org/3/library/bisect.html |
| Python `itertools` | https://docs.python.org/3/library/itertools.html |
| Python `functools` (`lru_cache`/`cache` for DP) | https://docs.python.org/3/library/functools.html |
| Python sorting how-to (key functions) | https://docs.python.org/3/howto/sorting.html |
| Python time complexity of built-ins | https://wiki.python.org/moin/TimeComplexity |
| Big-O cheat sheet | https://www.bigocheatsheet.com/ |
| NumPy for beginners | https://numpy.org/doc/stable/user/absolute_beginners.html ; routines index https://numpy.org/doc/stable/reference/routines.html |
| pandas 10 minutes | https://pandas.pydata.org/docs/user_guide/10min.html |
| pandas official cheat sheet (PDF) | https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf |
| pandas versus SQL | https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html |
| pandas groupby / window (rolling, expanding) | https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html ; https://pandas.pydata.org/docs/user_guide/window.html |
| scipy.stats | https://docs.scipy.org/doc/scipy/reference/stats.html ; t-test https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html |
| statsmodels stats (power, proportions) | https://www.statsmodels.org/stable/stats.html ; z-test for proportions https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html |
| Google Colab | https://colab.research.google.com/ (Google sign-in needed to run notebooks) |

See `DATASETS.md` for the practice datasets, which are downloaded into `exam_prep/data/`.
