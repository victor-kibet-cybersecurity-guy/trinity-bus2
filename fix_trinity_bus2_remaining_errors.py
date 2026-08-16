from pathlib import Path
import re
import struct
import zlib
import sys

ROOT = Path.cwd()

CSS_FILES = [
    ROOT / "css" / "enhancements.min.css",
    ROOT / "css" / "site-responsive.css",
    ROOT / "css" / "site.bundle.min.css",
    ROOT / "css" / "site.min.css",
]

def write_text(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

def remove_text_size_adjust():
    changed = 0
    removed = 0

    for path in CSS_FILES:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text

        text, n1 = re.subn(
            r'-webkit-text-size-adjust\s*:\s*[^;}{]+;?',
            '',
            text,
            flags=re.I
        )

        # Remove standard text-size-adjust too, so Edge Tools does not replace
        # the severity-8 warning with a separate compatibility warning.
        text, n2 = re.subn(
            r'(?<!-webkit-)\btext-size-adjust\s*:\s*[^;}{]+;?',
            '',
            text,
            flags=re.I
        )

        if text != original:
            write_text(path, text)
            changed += 1
            removed += n1 + n2

    return changed, removed

def create_png_icon(path, width=180, height=180):
    path.parent.mkdir(parents=True, exist_ok=True)

    # Simple Trinity-style touch icon using only Python standard library.
    # Dark background with a white T.
    bg = (14, 24, 38, 255)
    fg = (255, 255, 255, 255)

    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            pixel = bg

            # Top bar of T
            if 42 <= y <= 72 and 36 <= x <= 144:
                pixel = fg

            # Stem of T
            if 75 <= y <= 145 and 76 <= x <= 104:
                pixel = fg

            row.extend(pixel)

        rows.append(b"\x00" + bytes(row))

    raw = b"".join(rows)

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )

    path.write_bytes(png)

def fix_apple_touch_icon():
    partial = ROOT / "scripts" / "partials" / "header-snippet.html"
    if not partial.exists():
        return False, "header-snippet.html missing"

    icon_path = ROOT / "icons" / "apple-touch-icon.png"
    create_png_icon(icon_path)

    text = partial.read_text(encoding="utf-8", errors="ignore")
    tag = '<link rel="apple-touch-icon" sizes="180x180" href="<!--ROOT-->icons/apple-touch-icon.png">'

    if re.search(r'<link\b[^>]*rel=["\']apple-touch-icon["\'][^>]*>', text, flags=re.I):
        text = re.sub(
            r'<link\b[^>]*rel=["\']apple-touch-icon["\'][^>]*>',
            tag,
            text,
            count=1,
            flags=re.I
        )
    else:
        favicon_match = re.search(
            r'<link\b[^>]*rel=["\']icon["\'][^>]*>',
            text,
            flags=re.I
        )
        if favicon_match:
            pos = favicon_match.end()
            text = text[:pos] + "\n  " + tag + text[pos:]
        else:
            text = re.sub(
                r'</head>',
                '  ' + tag + '\n</head>',
                text,
                count=1,
                flags=re.I
            )

    write_text(partial, text)
    return True, "Apple touch icon fixed"

def fix_routes_inline_style():
    routes = ROOT / "routes.html"
    css = ROOT / "css" / "site.min.css"

    if not routes.exists() or not css.exists():
        return False, "routes.html or css/site.min.css missing"

    html = routes.read_text(encoding="utf-8", errors="ignore")
    original = html

    html = html.replace(
        'class="card" hidden style="text-align:center;padding:40px;margin-top:20px;"',
        'class="card route-no-results" hidden'
    )

    if html == original:
        html = re.sub(
            r'class=(["\'])card\1\s+hidden\s+style=(["\'])text-align\s*:\s*center\s*;\s*padding\s*:\s*40px\s*;\s*margin-top\s*:\s*20px\s*;?\2',
            'class="card route-no-results" hidden',
            html,
            count=1,
            flags=re.I
        )

    if html != original:
        write_text(routes, html)

    css_text = css.read_text(encoding="utf-8", errors="ignore")
    rule = ".route-no-results{text-align:center;padding:40px;margin-top:20px;}"

    if ".route-no-results{" not in css_text.replace(" ", ""):
        if not css_text.endswith("\n"):
            css_text += "\n"
        css_text += "\n/* Route results empty state */\n" + rule + "\n"
        write_text(css, css_text)

    return True, "routes.html inline style moved to css/site.min.css"

def delete_bak_files():
    deleted = []
    failed = []

    for path in ROOT.rglob("*.bak"):
        if not path.is_file():
            continue
        try:
            path.unlink()
            deleted.append(path.relative_to(ROOT).as_posix())
        except Exception as exc:
            failed.append((path.relative_to(ROOT).as_posix(), str(exc)))

    return deleted, failed

def validate():
    problems = []

    for path in CSS_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")

        if re.search(r'-webkit-text-size-adjust\s*:', text, flags=re.I):
            problems.append(f"{path.relative_to(ROOT)} still contains -webkit-text-size-adjust")

        if re.search(r'(?<!-webkit-)\btext-size-adjust\s*:', text, flags=re.I):
            problems.append(f"{path.relative_to(ROOT)} still contains text-size-adjust")

    partial = ROOT / "scripts" / "partials" / "header-snippet.html"
    if partial.exists():
        text = partial.read_text(encoding="utf-8", errors="ignore")
        if 'rel="apple-touch-icon"' not in text:
            problems.append("apple-touch-icon link is missing")
        if "apple-touch-icon.png" not in text:
            problems.append("apple-touch-icon does not point to PNG")

    if not (ROOT / "icons" / "apple-touch-icon.png").exists():
        problems.append("icons/apple-touch-icon.png was not created")

    routes = ROOT / "routes.html"
    if routes.exists():
        text = routes.read_text(encoding="utf-8", errors="ignore")
        if 'id="routeNoResults"' in text and 'style=' in re.search(
            r'<div[^>]*id=["\']routeNoResults["\'][^>]*>',
            text,
            flags=re.I
        ).group(0):
            problems.append("routeNoResults still has inline style")

    bak_left = [p for p in ROOT.rglob("*.bak") if p.is_file()]
    if bak_left:
        problems.append(f"{len(bak_left)} .bak file(s) remain")

    if problems:
        print("\nVALIDATION FAILED")
        for item in problems:
            print(" -", item)
        return 1

    print("\nValidation passed.")
    return 0

def main():
    if not (ROOT / "index.html").exists():
        print("Run this script from the TRINITY-BUS2 project root.")
        return 2

    css_changed, declarations_removed = remove_text_size_adjust()
    icon_ok, icon_message = fix_apple_touch_icon()
    route_ok, route_message = fix_routes_inline_style()
    deleted, failed = delete_bak_files()

    print("Trinity Bus Express Problems cleanup:")
    print(f" - CSS files updated: {css_changed}")
    print(f" - text-size-adjust declarations removed: {declarations_removed}")
    print(f" - {icon_message}")
    print(f" - {route_message}")
    print(f" - .bak files deleted: {len(deleted)}")

    if deleted:
        for name in deleted:
            print(f"   deleted: {name}")

    if failed:
        print(f" - .bak files that could not be deleted: {len(failed)}")
        for name, error in failed:
            print(f"   failed: {name}: {error}")

    return validate()

if __name__ == "__main__":
    sys.exit(main())
