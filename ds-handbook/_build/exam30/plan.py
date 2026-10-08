"""Master plan for the 30-day exam exam plan. Single source of truth for builders and the website.

Algorithms: 3 problems a day from 3 DIFFERENT patterns (interleaving). Builders may swap a problem for a more
company-frequent one (see RESOURCES.md) only if it keeps the same pattern, difficulty and is not used elsewhere.
SQL / stats / AI: `focus` = today's new topic(s); `review` = earlier topics that get 1 to 2 interleaved questions.
"""

LEVEL = {d: ("easy" if d <= 10 else "medium" if d <= 20 else "hard") for d in range(1, 31)}
MOCK_DAYS = {7, 14, 21, 28}          # timed mock exam days (same 4 notebooks, exam conditions)
FULL_LOOP_DAY = 29                   # full exam loop
LIGHT_DAY = 30                       # light day: redo the mistake log, behavioral prep, final check

# ---------------------------------------------------------------- website sections (ids are fixed: links depend on them)
SECTIONS = {
    "algo": ["recognize", "big-o", "arrays-strings", "hashing", "two-pointers", "sliding-window", "stack",
             "monotonic-stack", "binary-search", "sorting-intervals", "greedy", "prefix-sum", "heap", "linked-list",
             "trees", "bst", "graphs-bfs-dfs", "grid-simulation", "topological-sort", "union-find", "shortest-path",
             "backtracking", "dp-1d", "dp-2d", "design", "data-processing"],
    "sql": ["exam-approach", "query-order", "basics", "aggregation", "joins", "left-join-nulls", "case-when",
            "subqueries", "cte", "dates", "window-ranking", "top-n", "lag-lead", "running-totals", "self-join",
            "retention", "funnels", "ratios", "gaps-islands", "dedup-cleaning", "pivot", "median-percentiles",
            "recursive-cte", "pandas-equivalents"],
    "stats": ["case-framework", "descriptive", "probability", "bayes", "distributions", "clt-se",
              "confidence-intervals", "hypothesis-tests", "choosing-a-test", "power-mde", "ab-design",
              "ab-analysis", "ab-pitfalls", "ratio-metrics", "cuped", "regression", "causal-did",
              "causal-psm-rd-iv", "product-metrics", "metric-drop", "launch-decisions", "network-effects",
              "bayesian-sequential", "heterogeneous-effects", "probability-puzzles"],
    "ai": ["ml-framing", "bias-variance", "linear-regression", "logistic-regression", "classification-metrics",
           "regularization-cv", "trees-boosting", "features-imbalance", "unsupervised", "gradient-descent",
           "neural-networks", "embeddings", "recommenders", "nlp-basics", "attention-transformer",
           "pretraining-decoding", "fine-tuning-rlhf", "rag", "agents", "llm-evaluation", "ml-system-design",
           "deployment-monitoring", "safety-cost"],
    "cheat": ["python", "numpy", "pandas", "sql", "big-o", "algo-patterns", "stats-tests", "ab-testing",
              "ml-models", "ml-metrics", "deep-learning", "llm", "colab", "exam-day"],
}

# ---------------------------------------------------------------- algorithms: (LeetCode number, title, difficulty, pattern)
ALGO = {
    1:  [(1, "Two Sum", "easy", "hashing"), (125, "Valid Palindrome", "easy", "two-pointers"),
         (20, "Valid Parentheses", "easy", "stack")],
    2:  [(217, "Contains Duplicate", "easy", "hashing"), (704, "Binary Search", "easy", "binary-search"),
         (121, "Best Time to Buy and Sell Stock", "easy", "arrays-strings")],
    3:  [(242, "Valid Anagram", "easy", "hashing"), (206, "Reverse Linked List", "easy", "linked-list"),
         (104, "Maximum Depth of Binary Tree", "easy", "trees")],
    4:  [(283, "Move Zeroes", "easy", "two-pointers"), (1480, "Running Sum of 1d Array", "easy", "prefix-sum"),
         (21, "Merge Two Sorted Lists", "easy", "linked-list")],
    5:  [(643, "Maximum Average Subarray I", "easy", "sliding-window"), (226, "Invert Binary Tree", "easy", "trees"),
         (70, "Climbing Stairs", "easy", "dp-1d")],
    6:  [(387, "First Unique Character in a String", "easy", "hashing"),
         (35, "Search Insert Position", "easy", "binary-search"), (733, "Flood Fill", "easy", "graphs-bfs-dfs")],
    7:  [(169, "Majority Element", "easy", "hashing"), (88, "Merge Sorted Array", "easy", "two-pointers"),
         (1046, "Last Stone Weight", "easy", "heap")],
    8:  [(49, "Group Anagrams", "medium", "hashing"), (155, "Min Stack", "medium", "stack"),
         (100, "Same Tree", "easy", "trees")],
    9:  [(3, "Longest Substring Without Repeating Characters", "medium", "sliding-window"),
         (703, "Kth Largest Element in a Stream", "easy", "heap"), (141, "Linked List Cycle", "easy", "linked-list")],
    10: [(56, "Merge Intervals", "medium", "sorting-intervals"), (303, "Range Sum Query - Immutable", "easy", "prefix-sum"),
         (200, "Number of Islands", "medium", "graphs-bfs-dfs")],
    11: [(347, "Top K Frequent Elements", "medium", "heap"), (739, "Daily Temperatures", "medium", "monotonic-stack"),
         (15, "3Sum", "medium", "two-pointers")],
    12: [(560, "Subarray Sum Equals K", "medium", "prefix-sum"),
         (102, "Binary Tree Level Order Traversal", "medium", "trees"),
         (33, "Search in Rotated Sorted Array", "medium", "binary-search")],
    13: [(424, "Longest Repeating Character Replacement", "medium", "sliding-window"),
         (207, "Course Schedule", "medium", "topological-sort"), (198, "House Robber", "medium", "dp-1d")],
    14: [(128, "Longest Consecutive Sequence", "medium", "hashing"), (994, "Rotting Oranges", "medium", "graphs-bfs-dfs"),
         (875, "Koko Eating Bananas", "medium", "binary-search")],
    15: [(78, "Subsets", "medium", "backtracking"), (236, "Lowest Common Ancestor of a Binary Tree", "medium", "trees"),
         (435, "Non-overlapping Intervals", "medium", "greedy")],
    16: [(322, "Coin Change", "medium", "dp-1d"), (146, "LRU Cache", "medium", "design"),
         (11, "Container With Most Water", "medium", "two-pointers")],
    17: [(973, "K Closest Points to Origin", "medium", "heap"), (54, "Spiral Matrix", "medium", "grid-simulation"),
         (98, "Validate Binary Search Tree", "medium", "bst")],
    18: [(39, "Combination Sum", "medium", "backtracking"), (300, "Longest Increasing Subsequence", "medium", "dp-1d"),
         (547, "Number of Provinces", "medium", "union-find")],
    19: [(238, "Product of Array Except Self", "medium", "prefix-sum"),
         (1091, "Shortest Path in Binary Matrix", "medium", "graphs-bfs-dfs"),
         (621, "Task Scheduler", "medium", "greedy")],
    20: [(438, "Find All Anagrams in a String", "medium", "sliding-window"),
         (199, "Binary Tree Right Side View", "medium", "trees"),
         (1143, "Longest Common Subsequence", "medium", "dp-2d")],
    21: [(76, "Minimum Window Substring", "hard", "sliding-window"), (210, "Course Schedule II", "medium", "topological-sort"),
         (62, "Unique Paths", "medium", "dp-2d")],
    22: [(42, "Trapping Rain Water", "hard", "two-pointers"), (79, "Word Search", "medium", "backtracking"),
         (230, "Kth Smallest Element in a BST", "medium", "bst")],
    23: [(23, "Merge k Sorted Lists", "hard", "heap"), (72, "Edit Distance", "medium", "dp-2d"),
         (417, "Pacific Atlantic Water Flow", "medium", "graphs-bfs-dfs")],
    24: [(84, "Largest Rectangle in Histogram", "hard", "monotonic-stack"),
         (743, "Network Delay Time", "medium", "shortest-path"), (31, "Next Permutation", "medium", "arrays-strings")],
    25: [(295, "Find Median from Data Stream", "hard", "heap"), (51, "N-Queens", "hard", "backtracking"),
         (981, "Time Based Key-Value Store", "medium", "binary-search")],
    26: [(124, "Binary Tree Maximum Path Sum", "hard", "trees"), (127, "Word Ladder", "hard", "graphs-bfs-dfs"),
         (1004, "Max Consecutive Ones III", "medium", "sliding-window")],
    27: [(239, "Sliding Window Maximum", "hard", "monotonic-stack"), (416, "Partition Equal Subset Sum", "medium", "dp-1d"),
         (787, "Cheapest Flights Within K Stops", "medium", "shortest-path")],
    28: [(329, "Longest Increasing Path in a Matrix", "hard", "dp-2d"),
         (297, "Serialize and Deserialize Binary Tree", "hard", "trees"), (763, "Partition Labels", "medium", "greedy")],
    29: [(None, "Sessionize a click log (custom data-processing round)", "medium", "data-processing"),
         (41, "First Missing Positive", "hard", "hashing"), (1235, "Maximum Profit in Job Scheduling", "hard", "dp-1d")],
    30: [(None, "Top creators by watch time from raw event logs (custom)", "medium", "data-processing"),
         (853, "Car Fleet", "medium", "sorting-intervals")],
}

# ---------------------------------------------------------------- SQL / stats / AI: (focus topics, review topics); topics = section ids
SQL = {
    1: (["basics"], []), 2: (["aggregation"], ["basics"]), 3: (["joins"], ["aggregation"]),
    4: (["left-join-nulls"], ["joins"]), 5: (["case-when"], ["aggregation", "left-join-nulls"]),
    6: (["subqueries"], ["case-when"]), 7: (["mock"], ["basics", "aggregation", "joins", "left-join-nulls", "case-when", "subqueries"]),
    8: (["cte"], ["subqueries"]), 9: (["dates"], ["cte", "joins"]), 10: (["window-ranking"], ["dates"]),
    11: (["top-n"], ["window-ranking", "left-join-nulls"]), 12: (["lag-lead"], ["top-n"]),
    13: (["running-totals"], ["lag-lead", "dates"]), 14: (["mock"], ["cte", "dates", "window-ranking", "top-n", "lag-lead", "running-totals"]),
    15: (["self-join"], ["running-totals"]), 16: (["retention"], ["self-join", "dates"]),
    17: (["funnels"], ["retention", "case-when"]), 18: (["ratios"], ["funnels"]),
    19: (["gaps-islands"], ["lag-lead", "ratios"]), 20: (["dedup-cleaning"], ["gaps-islands", "top-n"]),
    21: (["mock"], ["self-join", "retention", "funnels", "ratios", "gaps-islands", "dedup-cleaning"]),
    22: (["pivot"], ["retention"]), 23: (["median-percentiles"], ["pivot", "funnels"]),
    24: (["recursive-cte"], ["median-percentiles", "gaps-islands"]), 25: (["company-style"], ["retention", "ratios"]),
    26: (["company-style"], ["top-n", "running-totals"]), 27: (["company-style"], ["dedup-cleaning", "self-join"]),
    28: (["mock"], ["company-style"]), 29: (["pandas-equivalents"], ["company-style"]), 30: (["final-review"], ["mistake-log"]),
}
STATS = {
    1: (["descriptive"], []), 2: (["probability"], ["descriptive"]), 3: (["bayes"], ["probability"]),
    4: (["distributions"], ["bayes"]), 5: (["clt-se"], ["distributions"]), 6: (["confidence-intervals"], ["clt-se"]),
    7: (["mock"], ["descriptive", "probability", "bayes", "distributions", "clt-se", "confidence-intervals"]),
    8: (["hypothesis-tests"], ["confidence-intervals"]), 9: (["choosing-a-test"], ["hypothesis-tests"]),
    10: (["power-mde"], ["choosing-a-test", "bayes"]), 11: (["ab-design"], ["power-mde"]),
    12: (["ab-analysis"], ["ab-design", "choosing-a-test"]), 13: (["ab-pitfalls"], ["ab-analysis"]),
    14: (["mock"], ["hypothesis-tests", "choosing-a-test", "power-mde", "ab-design", "ab-analysis", "ab-pitfalls"]),
    15: (["ratio-metrics"], ["ab-pitfalls"]), 16: (["cuped"], ["ratio-metrics", "power-mde"]),
    17: (["regression"], ["cuped"]), 18: (["causal-did"], ["regression"]), 19: (["causal-psm-rd-iv"], ["causal-did"]),
    20: (["product-metrics"], ["causal-psm-rd-iv", "ab-design"]),
    21: (["mock"], ["ratio-metrics", "cuped", "regression", "causal-did", "causal-psm-rd-iv", "product-metrics"]),
    22: (["metric-drop"], ["product-metrics"]), 23: (["launch-decisions"], ["metric-drop", "ab-pitfalls"]),
    24: (["network-effects"], ["launch-decisions"]), 25: (["probability-puzzles"], ["distributions", "bayes"]),
    26: (["bayesian-sequential"], ["ab-pitfalls", "probability-puzzles"]), 27: (["heterogeneous-effects"], ["regression", "launch-decisions"]),
    28: (["mock"], ["metric-drop", "launch-decisions", "network-effects", "probability-puzzles", "bayesian-sequential", "heterogeneous-effects"]),
    29: (["case-framework"], ["full-loop"]), 30: (["final-review"], ["mistake-log"]),
}
AI = {
    1: (["ml-framing"], []), 2: (["bias-variance"], ["ml-framing"]), 3: (["linear-regression"], ["bias-variance"]),
    4: (["logistic-regression"], ["linear-regression"]), 5: (["classification-metrics"], ["logistic-regression"]),
    6: (["regularization-cv"], ["classification-metrics", "bias-variance"]),
    7: (["mock"], ["ml-framing", "bias-variance", "linear-regression", "logistic-regression", "classification-metrics", "regularization-cv"]),
    8: (["trees-boosting"], ["regularization-cv"]), 9: (["features-imbalance"], ["trees-boosting", "classification-metrics"]),
    10: (["unsupervised"], ["features-imbalance"]), 11: (["gradient-descent"], ["unsupervised", "logistic-regression"]),
    12: (["neural-networks"], ["gradient-descent"]), 13: (["embeddings"], ["neural-networks"]),
    14: (["mock"], ["trees-boosting", "features-imbalance", "unsupervised", "gradient-descent", "neural-networks", "embeddings"]),
    15: (["recommenders"], ["embeddings"]), 16: (["nlp-basics"], ["recommenders"]),
    17: (["attention-transformer"], ["nlp-basics", "embeddings"]), 18: (["pretraining-decoding"], ["attention-transformer"]),
    19: (["fine-tuning-rlhf"], ["pretraining-decoding"]), 20: (["rag"], ["fine-tuning-rlhf", "embeddings"]),
    21: (["mock"], ["recommenders", "nlp-basics", "attention-transformer", "pretraining-decoding", "fine-tuning-rlhf", "rag"]),
    22: (["agents"], ["rag"]), 23: (["llm-evaluation"], ["agents", "classification-metrics"]),
    24: (["ml-system-design"], ["recommenders", "llm-evaluation"]), 25: (["ml-system-design"], ["features-imbalance"]),
    26: (["deployment-monitoring"], ["ml-system-design"]), 27: (["safety-cost"], ["deployment-monitoring", "llm-evaluation"]),
    28: (["mock"], ["agents", "llm-evaluation", "ml-system-design", "deployment-monitoring", "safety-cost"]),
    29: (["ml-system-design"], ["full-loop"]), 30: (["final-review"], ["mistake-log"]),
}
# day 24: ML system design case = feed ranking; day 25: content moderation / integrity; day 29: evaluate an AI feature end to end

NOTEBOOK_COUNTS = {"algorithms": 3, "sql": 5, "stats": 4, "ai": 5}   # questions per normal day (mocks: see builders)
THEORY_QA_PER_DAY = 8                                                 # website flashcards per day, all 4 areas mixed


def day_summary(d):
    """One line per area, used by the website plan tab and notebook headers."""
    return {
        "level": LEVEL[d], "mock": d in MOCK_DAYS,
        "algorithms": [f"{t} ({lvl})" for _, t, lvl, _ in ALGO[d]],
        "sql": SQL[d], "stats": STATS[d], "ai": AI[d],
    }


if __name__ == "__main__":
    import json
    # sanity checks: 3 different patterns per day, no repeated problems
    seen = set()
    for d, probs in ALGO.items():
        pats = [p[3] for p in probs]
        assert len(set(pats)) == len(pats), (d, pats)
        for p in probs:
            if p[0]:
                assert p[0] not in seen, p
                seen.add(p[0])
            assert p[3] in SECTIONS["algo"], p
    for table, tab in ((SQL, "sql"), (STATS, "stats"), (AI, "ai")):
        for d, (focus, review) in table.items():
            for t in focus + review:
                assert t in SECTIONS[tab] or t in ("mock", "company-style", "final-review", "mistake-log", "full-loop"), (tab, d, t)
    print("plan OK:", len(seen), "LeetCode problems")
    print(json.dumps(day_summary(1), indent=1))
