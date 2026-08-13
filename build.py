#!/usr/bin/env python3
"""Static-site generator for cmezabec.github.io.

Reads all content from data/cv.json and writes the HTML pages at the repo root.
No dependencies beyond the Python standard library.

    python3 build.py

Every page is regenerated from scratch, so do not hand-edit the generated .html
files: edit data/cv.json (or the templates in this file) and rebuild.
"""

import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "cv.json")

NAV = [
    ("index.html", "Home"),
    ("research.html", "Research"),
    ("projects.html", "Projects"),
    ("teaching.html", "Teaching"),
    ("talks.html", "Talks &amp; Visits"),
    ("cv.html", "CV"),
    ("contact.html", "Contact"),
]

# Old filenames kept alive as redirects so existing links do not break.
REDIRECTS = {
    "investigacion.html": "research.html",
    "docencia.html": "teaching.html",
    "contacto.html": "contact.html",
}

SITE_URL = "https://cmezabec.github.io"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def esc(s):
    """Escape text that must not be interpreted as HTML."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def nav_html(current):
    items = []
    for href, label in NAV:
        cls = ' class="active"' if href == current else ""
        items.append(f'<a href="{href}"{cls}>{label}</a>')
    return "\n      ".join(items)


def page(current, title, body, description=""):
    d = description or f"{title} — Cristian Meza, Full Professor of Statistics, Universidad de Valparaíso."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Cristian Meza</title>
<meta name="description" content="{esc(d)}">
<meta name="author" content="Cristian Meza">
<meta property="og:title" content="{esc(title)} — Cristian Meza">
<meta property="og:description" content="{esc(d)}">
<meta property="og:type" content="profile">
<meta property="og:url" content="{SITE_URL}/{current}">
<link rel="canonical" href="{SITE_URL}/{current}">
<link rel="stylesheet" href="assets/styles.css">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="container">
    <div class="brand">
      <div>
        <a class="name" href="index.html">Cristian Meza</a>
        <p class="tagline">Full Professor · INGEMAT–CIMFAV · Universidad de Valparaíso</p>
      </div>
    </div>
    <nav aria-label="Main">
      {nav_html(current)}
    </nav>
  </div>
</header>

<main class="container" id="main">
{body}
</main>

<footer class="site-footer">
  <div class="container">
    <p>© {date.today().year} Cristian Meza · INGEMAT–CIMFAV, Universidad de Valparaíso</p>
    <p class="muted">Last updated {date.today().isoformat()} · Built from <code>data/cv.json</code> · Hosted on GitHub Pages</p>
  </div>
</footer>
</body>
</html>
"""


def section(title, inner, extra_class=""):
    cls = "card" + (" " + extra_class if extra_class else "")
    h = f"<h2>{title}</h2>\n" if title else ""
    return f'<section class="{cls}">\n{h}{inner}\n</section>\n'


def pub_entry(p):
    """One bibliography entry."""
    bits = [f'<span class="authors">{p["authors"]}</span>']
    title = esc(p["title"])
    link = p.get("url") or (f'https://doi.org/{p["doi"]}' if p.get("doi") else "")
    if link:
        title = f'<a href="{link}">{title}</a>'
    bits.append(f'<span class="ptitle">{title}</span>')
    venue = f'<em>{esc(p["venue"])}</em>' if p.get("venue") else ""
    tail = ", ".join(x for x in [venue, esc(p["detail"]) if p.get("detail") else ""] if x)
    if tail:
        bits.append(f'<span class="venue">{tail}</span>')
    entry = ". ".join(bits) + "."
    year = f'<span class="year">{esc(p["year"])}</span>'
    return f'<li class="pub">{year}<div class="pubbody">{entry}</div></li>'


def dl_list(rows):
    """Definition-style two-column list: (left, right-html)."""
    out = ['<dl class="timeline">']
    for left, right in rows:
        out.append(f'<dt>{left}</dt><dd>{right}</dd>')
    out.append("</dl>")
    return "\n".join(out)


def group_by_year(items):
    """Yield (year, [items]) preserving the input order of years."""
    order, buckets = [], {}
    for it in items:
        y = it["year"]
        if y not in buckets:
            buckets[y] = []
            order.append(y)
        buckets[y].append(it)
    return [(y, buckets[y]) for y in order]


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def build_index(cv):
    p, c = cv["person"], cv["contact"]
    about = "\n".join(f"<p>{t}</p>" for t in cv["about"])

    links = " ".join(
        f'<a class="chip" href="{pr["url"]}" rel="me">{esc(pr["name"])}</a>'
        for pr in c["profiles"]
    )
    cv_link = (
        f'<a class="chip chip-primary" href="{p["cv_pdf"]}">Curriculum Vitae (PDF)</a>'
    )

    hero = f"""<div class="hero">
  <div class="hero-text">
    <h1>Cristian Meza</h1>
    <p class="lead">{esc(p["role"])} · {esc(p["affiliation"])}<br>{esc(p["faculty"])}</p>
    {about}
    <p class="chips">{cv_link} {links}</p>
  </div>
  <figure class="hero-photo">
    <img src="{p["photo"]}" alt="Portrait of Cristian Meza" width="220" height="219">
  </figure>
</div>"""

    interests = "<ul class=\"tags\">" + "".join(
        f"<li>{esc(i)}</li>" for i in cv["research_interests"]
    ) + "</ul>"

    # A short "selected recent work" teaser: the three most recent publications.
    recent = "<ul class=\"clean pubs\">" + "".join(
        pub_entry(x) for x in cv["publications"][:3]
    ) + "</ul>"
    recent += '<p class="more"><a href="research.html">All publications →</a></p>'

    current = [pr for pr in cv["projects"] if "202" in pr["years"].split("–")[-1]][:3]
    proj = dl_list([(esc(pr["years"]),
                     f'<strong>{esc(pr["title"])}</strong><br><span class="muted">{esc(pr["role"])} · {esc(pr["agency"])}</span>')
                    for pr in current])
    proj += '<p class="more"><a href="projects.html">All projects →</a></p>'

    body = (
        section("", hero, "hero-card")
        + section("Research interests", interests)
        + section("Recent publications", recent)
        + section("Current projects", proj)
    )
    return page("index.html", "Home", body,
                "Cristian Meza — Full Professor of Statistics at Universidad de Valparaíso. "
                "Mixed-effects models, SAEM algorithm, semiparametric and penalized methods.")


def build_research(cv):
    pubs = "<ul class=\"clean pubs\">" + "".join(pub_entry(x) for x in cv["publications"]) + "</ul>"
    confs = "<ul class=\"clean pubs\">" + "".join(pub_entry(x) for x in cv["conference_papers"]) + "</ul>"
    t = cv["thesis"]
    thesis = f'<p>{esc(t["author"])}. <em>{esc(t["title"])}</em>. {esc(t["detail"])}</p>'

    interests = "<ul class=\"tags\">" + "".join(
        f"<li>{esc(i)}</li>" for i in cv["research_interests"]
    ) + "</ul>"

    n = len(cv["publications"])
    intro = (f'<p>{n} peer-reviewed journal articles. A full list is also available on '
             f'<a href="{cv["contact"]["profiles"][1]["url"]}">Google Scholar</a> and '
             f'<a href="{cv["contact"]["profiles"][0]["url"]}">ORCID</a>.</p>')

    body = (
        section("Research interests", interests)
        + section("Journal articles", intro + pubs)
        + section("Conference papers and proceedings", confs)
        + section("PhD thesis", thesis)
    )
    return page("research.html", "Research", body,
                "Publications of Cristian Meza: mixed-effects models, SAEM algorithm, "
                "segmentation, penalized estimation, biostatistics and astrostatistics.")


def build_projects(cv):
    rows = [(esc(pr["years"]),
             f'<strong>{esc(pr["title"])}</strong><br>'
             f'<span class="muted">{esc(pr["role"])} · {esc(pr["agency"])}</span>')
            for pr in cv["projects"]]
    resp = dl_list([(esc(r["years"]), r["text"]) for r in cv["responsibilities"]])

    body = (
        section("Research projects and funding", dl_list(rows))
        + section("Institutional responsibilities", resp)
    )
    return page("projects.html", "Projects", body,
                "Research projects and funding of Cristian Meza: FONDECYT, MATH-AmSud, "
                "INRIA associate teams and institutional roles.")


def build_teaching(cv):
    t = cv["teaching"]
    grad = "<ul class=\"clean\">" + "".join(f"<li>{esc(x)}</li>" for x in t["graduate"]) + "</ul>"
    ugrad = "<ul class=\"clean\">" + "".join(f"<li>{esc(x)}</li>" for x in t["undergraduate"]) + "</ul>"

    s = cv["supervision"]
    phd = dl_list([(esc(x["year"]),
                    f'<strong>{esc(x["name"])}</strong><br><span class="muted">{esc(x["program"])}</span>')
                   for x in s["phd"]])

    body = (
        section("Teaching", f'<p>{esc(t["note"])}</p>')
        + section("Graduate courses", grad)
        + section("Undergraduate courses", ugrad)
        + section("PhD students supervised", phd + f'<p class="muted">{esc(s["msc_note"])}</p>')
    )
    return page("teaching.html", "Teaching", body,
                "Courses and student supervision by Cristian Meza at Universidad de Valparaíso.")


def build_talks(cv):
    talks = []
    for year, group in group_by_year(cv["talks"]):
        inner = "".join(
            f'<li><span class="ptitle">“{esc(x["title"])}”</span><br>'
            f'<span class="muted">{esc(x["event"])}</span></li>'
            for x in group
        )
        talks.append(f'<h3 class="yr">{esc(year)}</h3><ul class="clean spaced">{inner}</ul>')
    talks_html = "\n".join(talks)

    vis = []
    for year, group in group_by_year(cv["visiting"]):
        inner = "".join(
            f'<li>{esc(x["place"])} <span class="muted">({esc(x["when"])})</span></li>'
            for x in group
        )
        vis.append(f'<h3 class="yr">{esc(year)}</h3><ul class="clean">{inner}</ul>')
    vis_html = "\n".join(vis)

    body = (
        section("Invited talks and presentations", talks_html)
        + section("Visiting positions", '<p class="muted">Visiting professor / research stays.</p>' + vis_html)
    )
    return page("talks.html", "Talks &amp; Visits", body,
                "Invited talks, conference presentations and visiting research stays of Cristian Meza.")


def build_cv(cv):
    p = cv["person"]
    edu = dl_list([(esc(e["years"]),
                    f'<strong>{esc(e["degree"])}</strong><br>'
                    f'<span class="muted">{esc(e["institution"])}</span>'
                    + (f'<br>{e["note"]}' if e["note"] else ""))
                   for e in cv["education"]])
    pos = dl_list([(esc(x["years"]),
                    f'<strong>{esc(x["title"])}</strong><br><span class="muted">{esc(x["place"])}</span>')
                   for x in cv["positions"]])
    awards = dl_list([(esc(a["years"]), esc(a["text"])) for a in cv["awards"]])
    soc = "<ul class=\"clean\">" + "".join(f"<li>{esc(x)}</li>" for x in cv["societies"]) + "</ul>"
    skills = "<ul class=\"tags\">" + "".join(f"<li>{esc(x)}</li>" for x in cv["skills"]) + "</ul>"

    dl = (f'<p class="chips"><a class="chip chip-primary" href="{p["cv_pdf"]}">'
          f'Download full CV (PDF, {esc(p["cv_date"])})</a></p>')

    body = (
        section("Curriculum Vitae", dl)
        + section("Education", edu)
        + section("Academic positions", pos)
        + section("Awards and scholarships", awards)
        + section("Scientific societies", soc)
        + section("Computational skills", skills)
    )
    return page("cv.html", "CV", body,
                "Curriculum vitae of Cristian Meza: education, academic positions, awards and skills.")


def build_contact(cv):
    c = cv["contact"]
    addr = "<br>".join(esc(x) for x in c["address_lines"])
    prof = "<ul class=\"clean\">" + "".join(
        f'<li><a href="{pr["url"]}" rel="me">{esc(pr["name"])}</a> '
        f'<span class="muted">{esc(pr["handle"])}</span></li>' for pr in c["profiles"]
    ) + "</ul>"

    info = f"""<div class="grid2">
  <div>
    <h3>Address</h3>
    <p>{addr}</p>
  </div>
  <div>
    <h3>Office</h3>
    <p>Phone: {esc(c["phone"])}<br>
    Secretary (CIMFAV): {esc(c["phone_secretary"])}<br>
    E-mail: <a href="mailto:{c["email"]}">{esc(c["email"])}</a></p>
  </div>
</div>"""

    body = section("Contact", info) + section("Online profiles", prof)
    return page("contact.html", "Contact", body,
                "Contact details for Cristian Meza, INGEMAT–CIMFAV, Universidad de Valparaíso.")


def build_redirect(target):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{SITE_URL}/{target}">
<title>Redirecting…</title>
</head>
<body><p>This page has moved to <a href="{target}">{target}</a>.</p></body>
</html>
"""


# --------------------------------------------------------------------------

def main():
    with open(DATA, encoding="utf-8") as f:
        cv = json.load(f)

    pages = {
        "index.html": build_index(cv),
        "research.html": build_research(cv),
        "projects.html": build_projects(cv),
        "teaching.html": build_teaching(cv),
        "talks.html": build_talks(cv),
        "cv.html": build_cv(cv),
        "contact.html": build_contact(cv),
    }
    for old, new in REDIRECTS.items():
        pages[old] = build_redirect(new)

    for name, html in pages.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"wrote {name}")

    urls = [u for u in pages if u not in REDIRECTS]
    today = date.today().isoformat()
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(f"  <url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod></url>\n"
                         for u in urls)
               + "</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("wrote sitemap.xml")


if __name__ == "__main__":
    main()
