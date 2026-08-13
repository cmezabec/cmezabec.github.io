#!/usr/bin/env python3
"""Fill missing DOIs in data/cv.json by querying Crossref.

Only writes a DOI when the Crossref title is a close match to ours (>= 0.90
similarity), so it will not silently attach the wrong paper. Run it after adding
new entries:

    python3 tools/fill_dois.py           # dry run, shows what it would change
    python3 tools/fill_dois.py --write   # apply

Then rebuild:  python3 build.py
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "cv.json")
MAILTO = "cristian.meza@uv.cl"   # Crossref asks for a contact in the User-Agent
THRESHOLD = 0.90


def norm(s):
    s = re.sub(r"<[^>]+>", "", s).lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s).strip()


def lookup(title, year):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": "3"})
    url = f"https://api.crossref.org/works?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": f"cmezabec.github.io (mailto:{MAILTO})"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            items = json.load(r)["message"]["items"]
    except Exception as e:
        print(f"    ! query failed: {e}")
        return None

    best, best_score = None, 0.0
    for it in items:
        ct = (it.get("title") or [""])[0]
        score = SequenceMatcher(None, norm(title), norm(ct)).ratio()
        if score > best_score:
            best, best_score = it, score
    if best and best_score >= THRESHOLD:
        return best["DOI"], best_score, (best.get("title") or [""])[0]
    if best:
        print(f"    ~ best match only {best_score:.2f}: {(best.get('title') or [''])[0][:70]}")
    return None


def main():
    write = "--write" in sys.argv
    with open(DATA, encoding="utf-8") as f:
        cv = json.load(f)

    found = 0
    for key in ("publications", "conference_papers"):
        for p in cv[key]:
            if p.get("doi") or p.get("url"):
                continue
            print(f"  {p['year']}  {p['title'][:65]}")
            res = lookup(p["title"], p["year"])
            if res:
                doi, score, ct = res
                print(f"    -> {doi}  ({score:.2f})")
                p["doi"] = doi
                found += 1
            time.sleep(0.5)   # be polite to the API

    print(f"\n{found} DOI(s) found.")
    if write and found:
        with open(DATA, "w", encoding="utf-8") as f:
            json.dump(cv, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"wrote {DATA}  —  now run: python3 build.py")
    elif found:
        print("dry run — re-run with --write to apply.")


if __name__ == "__main__":
    main()
