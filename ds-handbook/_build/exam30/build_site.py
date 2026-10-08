"""Writes site/plan.json from plan.py and checks the content files (ids, links, JSON shape).
Run: python build_site.py   (prints problems; exit code 1 if any)"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plan import ALGO, SQL, STATS, AI, LEVEL, MOCK_DAYS, SECTIONS

SITE = os.path.join(HERE, "site")
TABS = ["algo", "sql", "stats", "ai", "cheat", "resources"]
LANGS = ["en", "fa", "ko"]


def lc_url(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower().replace("'", "")).strip("-")
    return f"https://leetcode.com/problems/{slug}/"


def write_plan():
    days = []
    for d in range(1, 31):
        days.append({
            "day": d, "level": LEVEL[d], "mock": d in MOCK_DAYS,
            "algo": [{"n": n, "title": (f"{n}. {t}" if n else t), "level": lvl, "pattern": pat,
                      "url": lc_url(t) if n else None} for n, t, lvl, pat in ALGO[d]],
            "sql": {"focus": SQL[d][0], "review": SQL[d][1]},
            "stats": {"focus": STATS[d][0], "review": STATS[d][1]},
            "ai": {"focus": AI[d][0], "review": AI[d][1]},
        })
    json.dump({"days": days}, open(os.path.join(SITE, "plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


LINK_FIXES = {   # dead or bot-blocked links found by the link check -> working pages
    "https://transparency.meta.com/reports/community-standards-enforcement/": "https://transparency.meta.com/reports/",
    "https://huyenchip.com/designing-machine-learning-systems/": "https://huyenchip.com/books/",
}


def fix_links():
    for path in glob.glob(os.path.join(SITE, "content", "*", "**", "*.json"), recursive=True):
        text = open(path, encoding="utf-8").read()
        new = text
        for a, b in LINK_FIXES.items():
            new = new.replace(a, b)
        if new != text:
            open(path, "w", encoding="utf-8").write(new)


def merge_parts():
    """content/<lang>/parts/<tab>_a.json + <tab>_b.json -> content/<lang>/<tab>.json (title/intro from the first part)."""
    for lang in LANGS:
        pdir = os.path.join(SITE, "content", lang, "parts")
        if not os.path.isdir(pdir):
            continue
        for tab in TABS:
            parts = sorted(f for f in os.listdir(pdir) if re.fullmatch(rf"{tab}_[a-z]\.json", f))
            if not parts:
                continue
            merged = {"title": "", "intro": "", "sections": []}
            for f in parts:
                d = json.load(open(os.path.join(pdir, f), encoding="utf-8"))
                merged["title"] = merged["title"] or d.get("title", "")
                merged["intro"] = merged["intro"] or d.get("intro", "")
                merged["sections"] += d.get("sections", [])
            if tab in SECTIONS:                       # keep the plan's order
                order = {f"{tab}-{s}": i for i, s in enumerate(SECTIONS[tab])}
                merged["sections"].sort(key=lambda s: order.get(s["id"], 999))
            json.dump(merged, open(os.path.join(SITE, "content", lang, tab + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)


SKELETON_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
:root { color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }
</style>
</head>
<body>
"""


def export_docs():
    """Standalone site in the ds-handbook folder of the personal website repository
    (served by GitHub Pages at https://mahsa-agz.github.io/ds-handbook/). Only index.html, app.js, plan.json and
    content/ are replaced; exam_prep/ and _build/ next to them are left alone."""
    import shutil
    docs = os.path.dirname(os.path.dirname(HERE))
    page = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
    open(os.path.join(docs, "index.html"), "w", encoding="utf-8").write(SKELETON_HEAD + page + "\n</body>\n</html>\n")
    for f in ("app.js", "plan.json"):
        shutil.copy(os.path.join(SITE, f), docs)
    for lang in LANGS:
        os.makedirs(os.path.join(docs, "content", lang), exist_ok=True)
        for tab in TABS + ["days", "ui"]:
            shutil.copy(os.path.join(SITE, "content", lang, tab + ".json"), os.path.join(docs, "content", lang))
    print("exported", docs)


def check_content():
    problems = []
    ids = {}
    for lang in LANGS:
        for tab in TABS + ["days", "ui"]:
            p = os.path.join(SITE, "content", lang, tab + ".json")
            if not os.path.exists(p):
                problems.append(f"missing {lang}/{tab}.json")
                continue
            try:
                data = json.load(open(p, encoding="utf-8"))
            except Exception as e:
                problems.append(f"bad JSON {lang}/{tab}.json: {e}")
                continue
            if tab in TABS:
                got = [s["id"] for s in data.get("sections", [])]
                if tab in SECTIONS:
                    want = [f"{tab}-{s}" for s in SECTIONS[tab]]
                    miss = [w for w in want if w not in got]
                    if miss:
                        problems.append(f"{lang}/{tab}: missing sections {miss}")
                for s in data.get("sections", []):
                    ids.setdefault(lang, set()).add(s["id"])
                    for k in ("title", "body"):
                        if not s.get(k):
                            problems.append(f"{lang}/{tab}/{s.get('id')}: empty {k}")
            if tab == "days":
                for d in data.get("days", []):
                    for qa in d.get("qa", []):
                        if not qa.get("q") or not qa.get("a"):
                            problems.append(f"{lang}/days/{d.get('day')}: empty q or a")
    # intra links must resolve
    for lang in LANGS:
        for tab in TABS + ["days"]:
            p = os.path.join(SITE, "content", lang, tab + ".json")
            if not os.path.exists(p):
                continue
            text = open(p, encoding="utf-8").read()
            for ref in set(re.findall(r"\]\(#([a-z0-9-]+)\)", text)) | set(re.findall(r'"ref": "([a-z0-9-]+)"', text)):
                if ref not in ids.get(lang, set()) and not ref.startswith("day-") and ref not in ("plan", "qa", "algo", "sql", "stats", "ai", "cheat", "resources"):
                    problems.append(f"{lang}/{tab}: broken link #{ref}")
    return problems


if __name__ == "__main__":
    write_plan()
    merge_parts()
    fix_links()
    probs = check_content()
    if not [p for p in probs if not p.startswith('missing')]:
        export_docs()
    for p in probs:
        print(p)
    print("plan.json written;", len(probs), "content problems")
    sys.exit(1 if [p for p in probs if not p.startswith("missing")] else 0)
