from pathlib import Path
import re
import sys

ROOT = Path.cwd()
LIVE_BASE = "https://victor-kibet-cybersecurity-guy.github.io/trinity-bus2"

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8", newline="\n")

def backup(path: Path):
    bak = path.with_suffix(path.suffix + ".bak")
    if path.exists() and not bak.exists():
        bak.write_bytes(path.read_bytes())

def fix_booking():
    path = ROOT / "booking.html"
    if not path.exists():
        return "booking.html missing"
    backup(path)
    text = read_text(path)

    if 'src="js/utils.js"' not in text:
        marker = '<script src="js/booking.js" defer></script>'
        replacement = '<script src="js/utils.js" defer></script>\n  ' + marker
        if marker in text:
            text = text.replace(marker, replacement, 1)
        else:
            return "booking.html found, booking.js marker missing"

    write_text(path, text)
    return "booking.html fixed"

def fix_404():
    path = ROOT / "404.html"
    if not path.exists():
        return "404.html missing"
    backup(path)
    text = read_text(path)
    text = re.sub(
        r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
        '<meta name="robots" content="noindex,follow">',
        text,
        count=1,
        flags=re.I,
    )
    write_text(path, text)
    return "404.html set to noindex,follow"

def fix_robots():
    path = ROOT / "robots.txt"
    if path.exists():
        backup(path)
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {LIVE_BASE}/sitemap.xml\n"
        f"Sitemap: {LIVE_BASE}/image-sitemap.xml\n"
    )
    write_text(path, content)
    return "robots.txt fixed"

def fix_sitemap():
    path = ROOT / "sitemap.xml"
    if not path.exists():
        return "sitemap.xml missing"
    backup(path)
    text = read_text(path)

    wrong_hosts = [
        "https://example.com/trinity-bus-express",
        "https://trinitybusexpress.com",
    ]
    for host in wrong_hosts:
        text = text.replace(host, LIVE_BASE)

    lines = text.splitlines()
    lines = [
        line for line in lines
        if not re.search(r"<loc>[^<]*/404\.html</loc>", line, flags=re.I)
    ]
    text = "\n".join(lines).rstrip() + "\n"
    write_text(path, text)
    return "sitemap.xml host fixed and 404 removed"

def fix_image_sitemap():
    path = ROOT / "image-sitemap.xml"
    if not path.exists():
        return "image-sitemap.xml missing"
    backup(path)
    text = read_text(path)
    text = text.replace("https://trinitybusexpress.com", LIVE_BASE)
    text = text.replace("https://example.com/trinity-bus-express", LIVE_BASE)
    write_text(path, text)
    return "image-sitemap.xml host fixed"

def add_homepage_seo():
    path = ROOT / "index.html"
    if not path.exists():
        return "index.html missing"
    backup(path)
    text = read_text(path)

    title_match = re.search(r"<title>(.*?)</title>", text, flags=re.I | re.S)
    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',
        text,
        flags=re.I | re.S,
    )
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else "Trinity Bus Express"
    desc = re.sub(r"\s+", " ", desc_match.group(1)).strip() if desc_match else "Trinity Bus Express cross-border travel information and booking requests."

    canonical = f"{LIVE_BASE}/"
    seo_block = (
        f'  <link rel="canonical" href="{canonical}">\n'
        '  <meta property="og:type" content="website">\n'
        '  <meta property="og:site_name" content="Trinity Bus Express">\n'
        f'  <meta property="og:title" content="{title}">\n'
        f'  <meta property="og:description" content="{desc}">\n'
        f'  <meta property="og:url" content="{canonical}">\n'
        f'  <meta property="og:image" content="{LIVE_BASE}/images/hero.jpeg">\n'
        '  <meta name="twitter:card" content="summary_large_image">\n'
        f'  <meta name="twitter:title" content="{title}">\n'
        f'  <meta name="twitter:description" content="{desc}">\n'
        f'  <meta name="twitter:image" content="{LIVE_BASE}/images/hero.jpeg">\n'
    )

    if 'rel="canonical"' not in text.lower():
        robots_match = re.search(
            r'(<meta\s+name=["\']robots["\'][^>]*>\s*)',
            text,
            flags=re.I,
        )
        if robots_match:
            pos = robots_match.end()
            text = text[:pos] + "\n" + seo_block + text[pos:]
        else:
            text = text.replace("</title>", "</title>\n" + seo_block, 1)
    else:
        text = re.sub(
            r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
            f'<link rel="canonical" href="{canonical}">',
            text,
            count=1,
            flags=re.I,
        )

    write_text(path, text)
    return "index.html canonical and social metadata added"

def validate():
    problems = []

    booking = ROOT / "booking.html"
    if booking.exists():
        t = read_text(booking)
        pos_utils = t.find('src="js/utils.js"')
        pos_booking = t.find('src="js/booking.js"')
        if pos_utils < 0 or pos_booking < 0 or pos_utils > pos_booking:
            problems.append("booking script dependency order is still wrong")

    robots = ROOT / "robots.txt"
    if robots.exists():
        t = read_text(robots)
        if "example.com" in t or "trinitybusexpress.com" in t:
            problems.append("robots.txt still has a wrong host")

    for name in ["sitemap.xml", "image-sitemap.xml"]:
        path = ROOT / name
        if path.exists():
            t = read_text(path)
            if "example.com" in t:
                problems.append(f"{name} still contains example.com")
            if "https://trinitybusexpress.com" in t:
                problems.append(f"{name} still contains trinitybusexpress.com")

    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists() and "/404.html</loc>" in read_text(sitemap):
        problems.append("sitemap.xml still lists 404.html")

    page404 = ROOT / "404.html"
    if page404.exists() and "noindex,follow" not in read_text(page404).replace(" ", "").lower():
        problems.append("404.html is not noindex,follow")

    if problems:
        print("\nValidation problems:")
        for p in problems:
            print(" -", p)
        return 1

    print("\nValidation passed.")
    return 0

def main():
    required = ["index.html", "booking.html", "404.html"]
    missing = [name for name in required if not (ROOT / name).exists()]
    if missing:
        print("Run this script from the trinity-bus2 project root.")
        print("Missing:", ", ".join(missing))
        return 2

    results = [
        fix_booking(),
        fix_404(),
        fix_robots(),
        fix_sitemap(),
        fix_image_sitemap(),
        add_homepage_seo(),
    ]

    print("Trinity Bus Express repair results:")
    for item in results:
        print(" -", item)

    return validate()

if __name__ == "__main__":
    sys.exit(main())
