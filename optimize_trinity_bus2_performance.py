from pathlib import Path
import re
import sys

ROOT = Path.cwd()

INDEX = ROOT / "index.html"
SITE_CSS = ROOT / "css" / "site.min.css"
SW = ROOT / "sw.js"

def read(path):
    return path.read_text(encoding="utf-8", errors="ignore")

def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

def optimize_homepage():
    if not INDEX.exists():
        return "index.html missing"

    text = read(INDEX)

    text = text.replace('href="images/coach-hero.svg" type="image/svg+xml"',
                        'href="images/hero.webp" type="image/webp"')
    text = text.replace('src="images/coach-hero.svg"', 'src="images/hero.webp"')

    text = re.sub(
        r'<link\s+rel=["\']preload["\']\s+as=["\']image["\'][^>]*>',
        '<link rel="preload" as="image" href="images/hero.webp" type="image/webp">',
        text,
        count=1,
        flags=re.I
    )

    if 'href="images/hero.webp" type="image/webp"' not in text:
        text = text.replace(
            '</head>',
            '  <link rel="preload" as="image" href="images/hero.webp" type="image/webp">\n</head>',
            1
        )

    text = re.sub(r'\s+fetchpriority=(["\'])high\1', '', text, flags=re.I)

    hero_pattern = re.compile(r'<img\b[^>]*class=["\']hero-bg["\'][^>]*>', re.I | re.S)
    hero_match = hero_pattern.search(text)
    if hero_match:
        tag = hero_match.group(0)
        if 'width=' not in tag:
            tag = tag[:-1] + ' width="1600">'
        if 'height=' not in tag:
            tag = tag[:-1] + ' height="900">'
        if 'decoding=' not in tag:
            tag = tag[:-1] + ' decoding="async">'
        tag = re.sub(r'\s+loading=(["\'])lazy\1', '', tag, flags=re.I)
        text = text[:hero_match.start()] + tag + text[hero_match.end():]

    text = re.sub(
        r'\.hero\{min-height:[^;]+;',
        '.hero{min-height:560px;',
        text,
        count=1
    )

    write(INDEX, text)
    return "homepage LCP optimized"

def optimize_css():
    if not SITE_CSS.exists():
        return "css/site.min.css missing"

    css = read(SITE_CSS)

    css = re.sub(
        r'\.hero(?:::after|:after)\{[^{}]*background:url\([^)]+coach-hero\.svg[^)]*\)[^{}]*\}',
        '',
        css,
        flags=re.I
    )

    css = css.replace('.hero{min-height:720px;', '.hero{min-height:560px;')
    css = css.replace('.hero{min-height:620px;', '.hero{min-height:560px;')

    perf_css = '''
/* === Trinity performance + responsive layer === */
.hero{min-height:560px}
.hero-bg{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  object-fit:cover;
  z-index:0
}
.homepage-hero:after{
  content:"";
  position:absolute;
  inset:0;
  background:linear-gradient(90deg,rgba(7,17,38,.88),rgba(7,17,38,.48));
  z-index:1
}
.homepage-hero .hero-content{position:relative;z-index:2}
.homepage-hero ~ section{
  content-visibility:auto;
  contain-intrinsic-size:700px
}
@media (max-width:900px){
  .site-header,
  .btn-secondary{
    -webkit-backdrop-filter:none!important;
    backdrop-filter:none!important
  }
}
@media (max-width:1024px){
  .container{width:min(100% - 32px,var(--max))}
  .search-panel{grid-template-columns:repeat(2,minmax(0,1fr))}
  .search-panel .btn{width:100%}
  .grid-4{grid-template-columns:repeat(2,minmax(0,1fr))}
  .footer-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:768px){
  html,body{max-width:100%;overflow-x:hidden}
  .hero{min-height:520px}
  .hero-content{width:min(100% - 24px,var(--max));padding:44px 0}
  h1{font-size:clamp(2rem,10vw,3.2rem)}
  h2{font-size:clamp(1.6rem,8vw,2.3rem)}
  .lead{font-size:1rem}
  .actions{gap:10px}
  .actions .btn{width:100%}
  .search-panel{
    grid-template-columns:1fr;
    gap:10px;
    padding:14px;
    border-radius:16px
  }
  .grid-2,.grid-3,.grid-4{grid-template-columns:1fr}
  .toolbar{grid-template-columns:1fr}
  .booking-layout{grid-template-columns:1fr}
  .form-grid{grid-template-columns:1fr}
  .summary{position:static}
  .comparison-wrapper{overflow-x:auto}
  .comparison-table{min-width:760px}
  .footer-grid{grid-template-columns:1fr}
  .section{padding:56px 0}
  .section-sm{padding:36px 0}
  .float-action{right:14px}
}
@media (max-width:480px){
  .container{width:calc(100% - 24px)}
  .hero{min-height:500px}
  .hero-content{width:calc(100% - 20px);padding:34px 0}
  .card{padding:18px}
  .btn{padding:.85rem 1rem}
  .site-header{padding-left:12px;padding-right:12px}
  .brand-logo{max-width:150px}
  .seat-map{transform:scale(.92);transform-origin:top center}
}
@media (max-width:360px){
  h1{font-size:1.9rem}
  .hero{min-height:480px}
  .search-panel{padding:10px}
  .btn{font-size:.92rem}
  .seat-map{transform:scale(.84)}
}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{
    animation-duration:.01ms!important;
    animation-iteration-count:1!important;
    scroll-behavior:auto!important;
    transition-duration:.01ms!important
  }
}
'''

    marker = "/* === Trinity performance + responsive layer === */"
    if marker in css:
        css = css[:css.index(marker)].rstrip() + "\n"
    css += "\n" + perf_css.strip() + "\n"

    write(SITE_CSS, css)
    return "responsive/performance CSS added"

def optimize_images():
    changed_files = 0
    upgraded_images = 0
    lazy_images = 0

    for path in ROOT.rglob("*.html"):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue

        text = read(path)
        original = text

        def repl(match):
            nonlocal upgraded_images, lazy_images
            tag = match.group(0)

            is_critical = (
                'class="brand-logo"' in tag
                or "class='brand-logo'" in tag
                or 'class="hero-bg"' in tag
                or "class='hero-bg'" in tag
            )

            src_match = re.search(r'src=(["\'])([^"\']+)\1', tag, flags=re.I)
            if src_match:
                src = src_match.group(2)

                if src.lower().endswith((".jpg", ".jpeg")):
                    src_path = (path.parent / src).resolve()
                    stem = src_path.with_suffix("")
                    webp640 = Path(str(stem) + "-640.webp")
                    webp1280 = Path(str(stem) + "-1280.webp")

                    if webp640.exists() and webp1280.exists():
                        rel640 = webp640.relative_to(path.parent.resolve()).as_posix()
                        rel1280 = webp1280.relative_to(path.parent.resolve()).as_posix()

                        tag = re.sub(
                            r'src=(["\'])[^"\']+\1',
                            f'src="{rel640}"',
                            tag,
                            count=1,
                            flags=re.I
                        )

                        if "srcset=" not in tag.lower():
                            tag = tag[:-1] + f' srcset="{rel640} 640w, {rel1280} 1280w" sizes="(max-width:768px) 100vw, 50vw">'

                        upgraded_images += 1

            if not is_critical:
                if "loading=" not in tag.lower():
                    tag = tag[:-1] + ' loading="lazy">'
                    lazy_images += 1
                if "decoding=" not in tag.lower():
                    tag = tag[:-1] + ' decoding="async">'
            else:
                tag = re.sub(r'\s+loading=(["\'])lazy\1', '', tag, flags=re.I)
                if "decoding=" not in tag.lower():
                    tag = tag[:-1] + ' decoding="async">'

            return tag

        text = re.sub(r'<img\b[^>]*>', repl, text, flags=re.I | re.S)

        if text != original:
            write(path, text)
            changed_files += 1

    return f"images optimized in {changed_files} HTML files, {upgraded_images} JPEGs upgraded, {lazy_images} lazy-load attributes added"

def optimize_service_worker():
    if not SW.exists():
        return "sw.js missing"

    text = read(SW)
    text = re.sub(r'const CACHE="[^"]+";', 'const CACHE="tbe-v6";', text, count=1)

    if '"./images/hero.webp"' not in text:
        text = text.replace(
            '"./images/trinity-express-logo.webp"',
            '"./images/trinity-express-logo.webp","./images/hero.webp"'
        )

    write(SW, text)
    return "service worker cache updated"

def remove_unused_fix_scripts():
    removed = 0
    for path in ROOT.glob("fix_trinity_bus2*.py"):
        try:
            path.unlink()
            removed += 1
        except Exception:
            pass
    return f"removed {removed} old repair scripts"

def validate():
    problems = []

    if INDEX.exists():
        t = read(INDEX)
        if 'src="images/hero.webp"' not in t:
            problems.append("homepage hero is not using hero.webp")
        if 'href="images/hero.webp"' not in t:
            problems.append("hero.webp preload missing")

    if SITE_CSS.exists():
        t = read(SITE_CSS)
        if "Trinity performance + responsive layer" not in t:
            problems.append("responsive performance CSS missing")
        if "content-visibility:auto" not in t:
            problems.append("content-visibility optimization missing")

    if SW.exists() and 'const CACHE="tbe-v6";' not in read(SW):
        problems.append("service worker cache version not updated")

    if problems:
        print("\nVALIDATION FAILED")
        for p in problems:
            print(" -", p)
        return 1

    print("\nValidation passed.")
    print("Commit and push the changed files, wait for GitHub Pages deployment, then test Lighthouse again.")
    return 0

def main():
    if not INDEX.exists() or not SITE_CSS.exists():
        print("Run this script from the TRINITY-BUS2 project root.")
        return 2

    print("Trinity Bus Express performance optimization:")
    print(" -", optimize_homepage())
    print(" -", optimize_css())
    print(" -", optimize_images())
    print(" -", optimize_service_worker())
    print(" -", remove_unused_fix_scripts())

    return validate()

if __name__ == "__main__":
    sys.exit(main())
