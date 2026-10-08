"""Shared setup snippets for the algorithm exam notebooks (algo_DD.py). Each string is pasted into the
notebook's setup cell, so every notebook stays self-contained in Colab."""

LIST_CODE = '''class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

def build_list(vals):
    """[1, 2, 3] -> 1 -> 2 -> 3 (returns the head, or None for an empty list)."""
    dummy = tail = ListNode()
    for v in vals:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

def list_values(head, limit=10000):
    """Linked list -> python list (stops after `limit` nodes in case of a cycle)."""
    out = []
    while head is not None and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out'''

TREE_CODE = '''from collections import deque

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

OPS_CODE = '''def check_ops(cls, ops, args, want):
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


def lc(slug):
    return f"https://leetcode.com/problems/{slug}/"
