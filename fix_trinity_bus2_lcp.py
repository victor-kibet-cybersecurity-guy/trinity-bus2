from pathlib import Path
import re
import sys

ROOT = Path.cwd()

INDEX = ROOT / "index.html"
CSS = ROOT / "css" / "site.min.css"

def read(path):
    return path.read_text(encoding="utf-8", errors="ignore")

def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

def backup(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".lcp.bak")
        if not bak.exists():
            bak.write_bytes(path.read_bytes())

def fix_index():
    if not INDEX.exists():
        return "index.html missing"

    backup(INDEX)
    text = read(INDEX)

    preload = '<link rel="preload" as="image" href="images/coach-hero.svg" type="image/svg+xml">'
    if preload not in text:
        insert_at = text.lower().find("</head>")
        if insert_at != -1:
            text = text[:insert_at] + "  " + preload + "\n" + text[insert_at:]

    text = re.sub(
        r'\.hero\{min-height:[^;]+;display:flex;align-items:center\}',
        '.hero{min-height:620px;display:grid;align-items:center;position:relative;overflow:hidden}',
        text,
        count=1
    )

    hero_open = '<section class="hero homepage-hero">'
    if hero_open in text and 'class="hero-bg"' not in text:
        replacement = '''<section class="hero homepage-hero">
      <img
        class="hero-bg"
        src="images/coach-hero.svg"
        width="1600"
        height="900"
        alt=""
        aria-hidden="true"
        decoding="async"
        fetchpriority="high">'''
        text = text.replace(hero_open, replacement, 1)

    if (ROOT / "icons" / "apple-touch-icon.png").exists():
        text = re.sub(
            r'<link\s+rel=["\']apple-touch-icon["\'][^>]*>',
            '<link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">',
            text,
            count=1,
            flags=re.I
        )

    write(INDEX, text)
    return "index.html updated"

def fix_css():
    if not CSS.exists():
        return "css/site.min.css missing"

    backup(CSS)
    text = read(CSS)

    text = re.sub(
        r'\.hero:after\{content:"";position:absolute;inset:0;background:url\([^)]+\)\s*center/cover\s*no-repeat;opacity:[^}]+\}',
        '',
        text,
        count=1
    )

    text = text.replace('.hero{min-height:720px;', '.hero{min-height:620px;', 1)

    additions = '''
.hero-bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}
.homepage-hero:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(7,17,38,.88),rgba(7,17,38,.55));z-index:1}
.homepage-hero .hero-content{position:relative;z-index:2}
@media(max-width:768px){.hero{min-height:580px}}
'''
    if '.hero-bg{' not in text:
        text += additions

    write(CSS, text)
    return "css/site.min.css updated"

def validate():
    problems = []

    if INDEX.exists():
        t = read(INDEX)
        if 'class="hero-bg"' not in t:
            problems.append("hero image element missing")
        if 'rel="preload" as="image" href="images/coach-hero.svg"' not in t:
            problems.append("hero preload missing")

    if CSS.exists():
        t = read(CSS)
        if "background:url('../images/coach-hero.svg')" in t:
            problems.append("old CSS hero background remains")
        if '.hero-bg{' not in t:
            problems.append("hero-bg CSS missing")

    if problems:
        print("\nVALIDATION FAILED")
        for p in problems:
            print(" -", p)
        return 1

    print("\nValidation passed.")
    return 0

def main():
    if not INDEX.exists() or not CSS.exists():
        print("Run this file from the TRINITY-BUS2 project root.")
        return 2

    print("LCP optimization:")
    print(" -", fix_index())
    print(" -", fix_css())

    return validate()

if __name__ == "__main__":
    sys.exit(main())
