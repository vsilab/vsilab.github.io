#!/usr/bin/env python3
"""Builds the VSI Lab website from the YAML files in _data/ into _site/.

You normally never run this yourself: GitHub runs it on every commit
(.github/workflows/deploy.yml). To preview on your own computer:

    pip install pyyaml
    python3 _build/build.py          # then open _site/index.html
"""
import html, os, shutil, sys
import yaml

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.path.join(ROOT, '_site')
e = lambda s: html.escape(str(s), quote=True)

def load(name):
    with open(os.path.join(ROOT, '_data', name + '.yml'), encoding='utf-8') as f:
        return yaml.safe_load(f)

SITE, PUBS, PEOPLE = load('site'), load('publications'), load('people')
RESEARCH, SERVICE, TEACH = load('research'), load('service'), load('teaching')
BY_TITLE = {p['title'].strip(): p for p in PUBS}
OWNER = 'Eungjoo Lee'

NAV = [('index', 'Home'), ('research', 'Research'), ('publications', 'Publications'),
       ('people', 'People'), ('teaching', 'Teaching'), ('resources', 'Resources')]
PUB_SECTIONS = [('to-appear', 'To Appear'), ('journal', 'Journal Articles'), ('conference', 'Conference Papers'),
                ('workshop', 'Workshop Papers'), ('chapter', 'Book Chapters'), ('abstract', 'Abstracts'),
                ('report', 'Technical Reports')]
ROLES = [('phd', 'Ph.D. Students'), ('ms', 'M.S. Students'), ('postbac', 'Post-Baccalaureate Researchers'),
         ('undergrad', 'Undergraduate Researchers'), ('collaborator', 'Affiliated Collaborators')]
ALUMNI_GROUPS = [('phd', 'Ph.D.'), ('ms', 'M.S.'), ('undergrad', 'Undergraduate'), ('visitor', 'Visitors')]

MODE = 'site'

# ───────────────────────── helpers ─────────────────────────
def href(page, anchor=''):
    if MODE == 'preview':
        return '#' + (anchor or ('top' if page == 'index' else page))
    return ('index.html' if page == 'index' else page + '.html') + ('#' + anchor if anchor else '')

def ext(url, text):
    return f'<a href="{e(url)}" target="_blank" rel="noopener">{text}</a>'

def section(title, body, sid='', cls=''):
    i = f' id="{sid}"' if sid else ''
    c = f' {cls}' if cls else ''
    return f'<section class="sec{c}"{i}><h2 class="sec-title">{title}</h2><div class="sec-body">{body}</div></section>'

def page_head(title, text):
    return f'<section class="page-head"><h1>{title}</h1><p>{text}</p></section>'

def venue_year(p):
    return f'{e(p["venue"])}, {e(p["year"])}'

def pub_links(p):
    out = []
    if p.get('url'):
        out.append(ext(p['url'], 'Preprint' if 'arxiv.org' in p['url'] else 'Paper'))
    if p.get('code'):
        out.append(ext(p['code'], 'Code'))
    if p.get('project'):
        out.append(ext(p['project'], 'Project page'))
    return out

def short_authors(a):
    """Lists of five or more authors are shortened to the first author plus 'et al., including Eungjoo Lee'."""
    if ', including ' in a:                       # already shortened in the data, e.g. "A, B, et al., including ..."
        head = a.split(', including ')[0]
        return f'{head.split(",")[0].strip()} et al., including {OWNER}' if 'et al' in head else a
    names = [n.strip() for n in a.split(',')]
    if len(names) < 5 or OWNER not in names:
        return a
    return f'{OWNER} et al.' if names[0] == OWNER else f'{names[0]} et al., including {OWNER}'


def pub_item(p):
    title = ext(p['url'], e(p['title'])) if p.get('url') else e(p['title'])
    short = short_authors(p['authors'])
    note_txt = p.get('note') or ''
    if short != p['authors'] and 'equal' in note_txt.lower():   # keep co-first authors visible when shortened
        n = [x.strip() for x in p['authors'].split(',')]
        short, note_txt = f'{n[0]} and {n[1]} (equal contribution) et al.', ''
    authors = e(short).replace(OWNER, f'<b>{OWNER}</b>')
    if note_txt.lower() == 'equal contribution':
        note_txt = 'first two authors contributed equally'
    note = f' <span class="pub-note">({e(note_txt)})</span>' if note_txt else ''
    links = pub_links(p)
    srch = e(' '.join(str(p.get(k, '')) for k in ('title', 'authors', 'venue', 'year')).lower())
    return (f'<li class="pub" data-search="{srch}"><span class="pub-year">{e(p["year"])}</span>'
            f'<div class="pub-body"><p class="pub-title">{title}</p><p class="pub-meta">{authors}{note}</p>'
            f'<p class="pub-meta"><i>{e(p["venue"])}</i></p>'
            + (f'<p class="pub-links">{"".join(links)}</p>' if links else '') + '</div></li>')

def figure(d):
    """Overview illustration for the home page. A missing file shows a blank panel instead of a broken image."""
    f = d.get('figure') or ''
    if os.path.exists(os.path.join(ROOT, 'assets', 'figures', f)):
        img = (f'<img src="assets/figures/{e(f)}" alt="{e(d.get("figure_alt", d["title"]))}" loading="lazy" decoding="async" '
               f'onerror="vsiFigError(this)">')
        cls = ''
    else:
        img, cls = '', ' is-empty'
    return f'<figure class="fig{cls}"><div class="fig-mat">{img}<span class="fig-empty" aria-hidden="true"></span></div></figure>'


def photo(file, name, cls='portrait'):
    if file:
        return f'<div class="{cls}"><img src="assets/people/{e(file)}" alt="{e(name)}" loading="lazy" decoding="async"></div>'
    ini = ''.join(w[0] for w in name.replace(',', '').split()[:2])
    return f'<div class="{cls} ph"><span>{e(ini)}</span></div>'

def header(active):
    items = ''.join(f'<a href="{href(k)}" data-nav="{k}"{" aria-current=\"page\"" if k == active else ""}>{e(n)}</a>'
                    for k, n in NAV)
    return (f'<header class="masthead"><div class="masthead-in">'
            f'<a class="brand" href="{href("index")}"><span class="mark" role="img" aria-label="VSI"></span>'
            f'<span class="brand-name">{e(SITE["lab_name"])}</span></a>'
            f'<button class="menu" type="button" aria-expanded="false" aria-controls="nav">Menu</button>'
            f'<nav id="nav" class="nav" aria-label="Main">{items}</nav></div></header>')

def footer():
    pi = SITE['pi']
    return (f'<footer class="foot"><div class="foot-in">'
            f'<div class="foot-lab"><span class="mark" role="img" aria-label="VSI"></span>'
            f'<p>{e(SITE["lab_name"])}<br>School of Electrical, Computing, and Software Engineering<br>University of Arizona</p></div>'
            f'<p>{"<br>".join(e(x) for x in SITE["address"])}</p>'
            f'<p><a href="mailto:{e(SITE["email"])}">{e(SITE["email"])}</a><br>{e(SITE["phone"])}</p>'
            f'<p>{ext(pi["scholar"], "Google Scholar")}<br>{ext(SITE["github"], "GitHub")}<br>{ext(SITE["wiki"], "Lab wiki")}</p>'
            f'</div><p class="foot-copy">© 2026 {e(SITE["lab_name"])}, University of Arizona</p></footer>')

# ───────────────────────── pages ─────────────────────────
def page_home():
    pi = SITE['pi']
    links = [ext(pi['scholar'], 'Google Scholar'), ext(pi['orcid'], 'ORCID'), f'<a href="mailto:{e(SITE["email"])}">{e(SITE["email"])}</a>']
    if pi.get('cv'):
        links.insert(0, ext(pi['cv'], 'Curriculum vitae'))
    pi_html = (f'<div class="pi"><div class="pi-text"><p class="pi-name">{e(pi["name"])}</p>'
               f'<p class="pi-roles">{"<br>".join(e(t) for t in pi["titles"])}</p>'
               + ''.join(f'<p>{e(b.strip())}</p>' for b in pi['bio'])
               + f'<p class="pi-links">{"".join(links)}</p></div>{photo(pi["photo"], pi["name"], "pi-photo portrait")}</div>')
    groups = ''.join(
        f'<div class="svc-group"><h3 class="minor">{e(g["title"])}</h3><ul class="svc">'
        + ''.join(f'<li><span class="svc-what"><span class="svc-name">{e(i["name"])}</span><span class="svc-role">{e(i["role"])}</span></span>'
                  f'<span class="svc-year">{e(i.get("years", ""))}</span></li>' for i in g['items']) + '</ul></div>'
        for g in SERVICE['groups'])
    rv = SERVICE['reviewer']
    rvhtml = (f'<div class="svc-rv"><h3 class="minor">Reviewer</h3>'
               f'<p class="rv"><span>Journals</span>{", ".join(e(x) for x in rv["journals"])}</p>'
               f'<p class="rv"><span>Conferences</span>{", ".join(e(x) for x in rv["conferences"])}</p></div>')
    dirs = ''.join(f'<article class="dir">{figure(d)}<h3><a href="{href("research", d["id"])}">{e(d["title"])}</a></h3>'
                   f'<p>{e(d["summary"])}</p></article>' for d in RESEARCH['directions'])
    return (f'<section class="hero"><h1>{e(SITE["statement"])}</h1><p>{e(SITE["intro"].strip())}</p>'
            f'<p class="join"><span>Join the lab.</span> {e(SITE["join"].strip())} <a href="mailto:{e(SITE["email"])}">{e(SITE["email"])}</a></p></section>'
            + section('Principal Investigator', pi_html, 'pi')
            + section('Academic and Professional Service', f'<div class="svc-grid">{groups}</div>{rvhtml}', 'service')
            + section('Current Research', f'<div class="dirs">{dirs}</div>'
                      f'<p class="sec-more"><a href="{href("research")}">More on our research</a></p>', 'current'))

def page_research():
    out = [page_head('Research', 'Our work follows three connected directions. Each is listed below with related papers.')]
    for d in RESEARCH['directions']:
        topics = ''.join(f'<li>{e(t)}</li>' for t in d['topics'])
        papers = ''
        for t in d.get('papers', []):
            p = BY_TITLE.get(t.strip())
            if not p:
                print(f'warning: research.yml lists a paper not found in publications.yml: {t}', file=sys.stderr)
                continue
            ttl = ext(p['url'], e(p['title'])) if p.get('url') else e(p['title'])
            status = ', to appear' if p.get('status') == 'to-appear' else ''
            papers += f'<li>{ttl}<span>{venue_year(p)}{status}</span></li>'
        out.append(section(e(d['title']),
            f'<div class="r-text"><p class="lead">{e(d["summary"])}</p><ul class="topics">{topics}</ul>'
            f'<h3 class="minor">Related papers</h3><ul class="r-papers">{papers}</ul></div>', d['id'], 'stack'))
    collab = ''.join(f'<li>{e(c)}</li>' for c in RESEARCH.get('collaborations', []))
    if collab:
        out.append(section('Collaborations', f'<p>Our clinical and academic partners include:</p><ul class="plain">{collab}</ul>', 'collaborations', 'stack'))
    return ''.join(out)

def page_publications():
    chips = ['<button type="button" class="chip" data-cat="" aria-pressed="true">All</button>']
    groups = []
    for key, label in PUB_SECTIONS:
        if key == 'to-appear':
            items = [p for p in PUBS if p.get('status') == 'to-appear']
        else:
            items = [p for p in PUBS if p.get('type') == key and p.get('status') != 'to-appear']
        if not items:
            continue
        items.sort(key=lambda p: -int(p['year']))
        chips.append(f'<button type="button" class="chip" data-cat="{key}" aria-pressed="false">{e(label)}</button>')
        groups.append(section(e(label), f'<ol class="pubs">{"".join(pub_item(p) for p in items)}</ol>', key, 'pub-group'))
    head = (f'<section class="page-head"><h1>Publications</h1><p>Titles link to the published version or preprint where one is available. '
            f'A complete record is on {ext(SITE["pi"]["scholar"], "Google Scholar")}.</p>'
            f'<div class="filters"><div class="chips" role="group" aria-label="Category">{"".join(chips)}</div>'
            f'<label class="search"><span class="visually-hidden">Search publications</span>'
            f'<input id="pub-q" type="search" placeholder="Search by title, author, or venue" autocomplete="off"></label></div></section>')
    return head + ''.join(groups) + '<p class="empty" id="pub-empty" hidden>No publications match this search.</p>'

def page_people():
    out = [page_head('People', 'Students, researchers, and collaborators in the lab.')]
    for role, label in ROLES:
        ms = [m for m in PEOPLE['members'] if m.get('role') == role]
        if not ms:
            continue
        cards = ''.join(f'<li class="person">{photo(m.get("photo"), m["name"])}<p class="p-name">{e(m["name"])}</p>'
                        f'<p class="p-dept">{e(m.get("program", ""))}</p>'
                        + (f'<p class="p-dept">{e(m["note"])}</p>' if m.get('note') else '') + '</li>' for m in ms)
        out.append(section(label, f'<ul class="people">{cards}</ul>', role))
    al = ''
    for g, label in ALUMNI_GROUPS:
        rows = [a for a in PEOPLE.get('alumni', []) if a.get('group') == g]
        if rows:
            al += (f'<div class="al-group"><h3 class="minor">{label}</h3><ul class="alumni">'
                   + ''.join(f'<li><span class="al-name">{e(a["name"])}</span><span>{e(a.get("years", ""))}</span>'
                             + (f'<span class="al-now">{e(a["now"])}</span>' if a.get('now') else '') + '</li>' for a in rows)
                   + '</ul></div>')
    out.append(section('Alumni', f'<div class="al-grid">{al}</div>', 'alumni'))
    return ''.join(out)

def page_teaching():
    courses = ''.join(f'<div class="item"><p class="item-code">{e(c["code"])}</p><h3 class="item-title">{e(c["title"])}</h3>'
                      f'<p class="item-meta">{e(c["detail"])}</p></div>' for c in TEACH['courses'])
    advising = ''.join(f'<li><span class="row-k">{e(a["year"])}</span><span>{e(a["text"])}</span></li>' for a in TEACH['advising'])
    return (page_head('Teaching', 'Courses and research advising.')
            + section('Courses', courses)
            + section('Independent Study and Research Advising', f'<ul class="rows">{advising}</ul>'))

def page_resources():
    return (page_head('Resources', 'Datasets, benchmarks, and software from the lab.')
            + section('Datasets and Benchmarks', '<p>We are preparing datasets and benchmarks in surgical video, ultrasound imaging, '
                      'visual question answering, and multiview and egocentric perception. Release details will be posted here.</p>')
            + section('Code', f'<p>Public repositories that accompany our papers are on {ext(SITE["github"], "GitHub")}.</p>')
            + section('Lab Wiki', f'<p>Onboarding, compute, and lab practices for members are on the {ext(SITE["wiki"], "lab wiki")}.</p>'))

PAGES = [('index', 'Home', page_home), ('research', 'Research', page_research), ('publications', 'Publications', page_publications),
         ('people', 'People', page_people), ('teaching', 'Teaching', page_teaching), ('resources', 'Resources', page_resources)]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap">')

def build_site():
    global MODE
    MODE = 'site'
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    desc = SITE['intro'].strip().split('. ')[0] + '.'
    for key, name, fn in PAGES:
        title = f'{SITE["lab_name"]}, University of Arizona' if key == 'index' else f'{name}, {SITE["lab_name"]}'
        doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website">
<link rel="icon" href="assets/favicon.png"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
{FONTS}<link rel="stylesheet" href="assets/style.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
{header(key)}
<main id="main" class="wrap">{fn()}</main>
{footer()}
<script src="assets/site.js"></script></body></html>
'''
        with open(os.path.join(OUT, 'index.html' if key == 'index' else key + '.html'), 'w', encoding='utf-8') as f:
            f.write(doc)

def build_preview(path):
    global MODE
    MODE = 'preview'
    views = ''.join(f'<div class="view" data-view="{k}" id="{"top" if k == "index" else k}"{"" if k == "index" else " hidden"}>{fn()}</div>'
                    for k, n, fn in PAGES)
    css = open(os.path.join(ROOT, 'assets', 'style.css'), encoding='utf-8').read()
    js = open(os.path.join(ROOT, 'assets', 'site.js'), encoding='utf-8').read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'''<title>VSI Lab Website</title>
<meta name="claude:viewport-fit-sides" content="cover">
{FONTS}<style>{css}</style>
<div data-preview="1"><a class="skip" href="#main">Skip to content</a>
{header('index')}
<main id="main" class="wrap">{views}</main>
{footer()}</div>
<script>window.VSI_PREVIEW=true;</script><script>{js}</script>
''')

if __name__ == '__main__':
    build_site()
    if len(sys.argv) > 1:
        build_preview(sys.argv[1])
    print('Built', OUT)
