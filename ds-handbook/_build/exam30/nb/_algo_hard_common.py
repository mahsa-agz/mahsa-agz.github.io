"""Shared setup code for the hard algorithm notebooks (days 21 to 30). Imported by algo_21.py ... algo_30.py.
Each string is pasted into the notebook's setup cell, so every notebook stays self-contained in Colab.
Helper names match the earlier notebooks (build_tree, tree_values, build_list, list_values, check_ops, check_big)."""

BIG = '''import random, signal, time

class _TooSlow(BaseException):
    pass

def _stop(signum, frame):
    raise _TooSlow()

def check_big(label, run, want, key=None, limit=1.0):
    """Big-input test (the input is not printed). run() calls your function.
    PASS only if the answer is right AND it finishes within `limit` seconds.
    In Colab (Linux) a run that takes longer than 3 * limit + 3 seconds is stopped, so a slow brute force cannot hang the notebook."""
    alarm = hasattr(signal, "setitimer")
    if alarm:
        old = signal.signal(signal.SIGALRM, _stop)
        signal.setitimer(signal.ITIMER_REAL, 3 * limit + 3)
    t = time.perf_counter()
    try:
        got = run()
        if key is not None:
            got = key(got)
    except _TooSlow:
        got = "stopped: too slow"
    except Exception as e:
        got = "error: " + repr(e)[:120]
    finally:
        if alarm:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
    sec = time.perf_counter() - t
    good = got == want
    fast = sec <= limit
    note = ("" if good else "  wrong answer" + (f" ({got})" if isinstance(got, str) else "")) + ("" if fast else "  too slow")
    print(("PASS " if good and fast else "FAIL ") + f"{label}: {sec:.2f}s (limit {limit}s)" + note)'''

OPS = '''def check_ops(cls, ops, args, want):
    """Runs a LeetCode-style list of calls on a class: ops[0] is the constructor, then one method per step.
    Prints PASS or FAIL for every call whose expected value is not None."""
    try:
        obj = cls(*args[0])
    except Exception as e:
        print("FAIL constructor raised", repr(e))
        return
    ok = total = 0
    for op, a, w in zip(ops[1:], args[1:], want[1:]):
        try:
            got = getattr(obj, op)(*a)
        except Exception as e:
            got = "error: " + repr(e)
        if w is None:
            continue
        total += 1
        good = got == w
        ok += good
        shown = ", ".join(repr(x) for x in a)
        print(("PASS " if good else "FAIL ") + f"{op}({shown}) -> {got!r}" + ("" if good else f"   expected {w!r}"))
    print(f"{ok}/{total} passed")'''

TREE = '''from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def build_tree(vals):
    """Level-order list with None for gaps (LeetCode style) -> root. [1, 2, 3, None, 4] means 2 has a right child 4."""
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    queue, i = deque([root]), 1
    while queue and i < len(vals):
        node = queue.popleft()
        for side in ("left", "right"):
            if i < len(vals) and vals[i] is not None:
                child = TreeNode(vals[i])
                setattr(node, side, child)
                queue.append(child)
            i += 1
    return root

def tree_values(root):
    """Root -> level-order list with None for gaps (trailing None removed)."""
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if not isinstance(node, TreeNode):
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out'''

LIST = '''class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

def build_list(vals):
    """[1, 2, 3] -> 1 -> 2 -> 3 (returns the head, or None for an empty list)."""
    dummy = tail = ListNode()
    for v in vals:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

def list_values(head, limit=10**7):
    """Linked list -> python list (stops after `limit` nodes in case of a cycle)."""
    out = []
    while head is not None and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out'''


def lc(slug):
    return f"https://leetcode.com/problems/{slug}/"


def compute(*codes, expr):
    """Runs code strings in one namespace and evaluates expr there (used to get the expected answer of a big test).
    Every big answer is also cross-checked against a brute force on small inputs inside the solutions."""
    ns = {}
    exec("import random", ns)
    for c in codes:
        exec(c, ns)
    return eval(expr, ns)


MOCK_INTRO = ("**Mock exam.** One timer for the whole notebook: **60 minutes** for all three questions. Work as in "
              "the real exam: say the plan out loud, code, then test by hand. Do not open any hint or solution "
              "until the 60 minutes are over. Then grade yourself: solved within time, solved late, or not solved, "
              "and write the result in the mistake log.")
