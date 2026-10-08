"""Shared setup code for the medium algorithm notebooks (days 11 to 20). Imported by algo_11.py ... algo_20.py."""

BIG = '''import time

def check_big(label, run, want, key=None, limit=1.0):
    """Larger test: run() calls your function. PASS only if the answer is right AND it finishes within limit seconds."""
    t = time.perf_counter()
    try:
        got = run()
    except Exception as e:
        got = "error: " + repr(e)[:120]
    sec = time.perf_counter() - t
    try:
        good = (key(got) == key(want)) if (key and not isinstance(got, str)) else got == want
    except Exception:
        good = False
    fast = sec <= limit
    note = ("" if good else "  wrong answer" + (f" ({got})" if isinstance(got, str) else "")) + ("" if fast else "  too slow")
    print(("PASS " if good and fast else "FAIL ") + f"{label}: {sec:.2f}s (limit {limit}s)" + note)

def any_order(result):
    """Key for check(): ignores the order of the items and of the values inside each item."""
    try:
        return sorted(tuple(sorted(x)) if isinstance(x, (list, tuple)) else x for x in result)
    except TypeError:
        return result

def rows_any_order(result):
    """Key for check(): ignores the order of the items but keeps each item as it is (e.g. points [x, y])."""
    try:
        return sorted(tuple(x) for x in result)
    except TypeError:
        return result'''

TREE = '''from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def build(values):
    """Level-order list (None = missing child) -> root TreeNode, the same format LeetCode uses."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q, i = deque([root]), 1
    while q and i < len(values):
        node = q.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i]); q.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i]); q.append(node.right)
        i += 1
    return root

def find(root, val):
    """Returns the node with this value (values are unique in the tests)."""
    stack = [root]
    while stack:
        node = stack.pop()
        if node:
            if node.val == val:
                return node
            stack += [node.left, node.right]
    return None'''
