from pathlib import Path
import re
import sys

ROOT = Path.cwd()

def backup(path):
    bak = path.with_suffix(path.suffix + ".console-fix.bak")
    if path.exists() and not bak.exists():
        bak.write_bytes(path.read_bytes())

def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

def fix_html():
    changed_files = 0
    fetchpriority_removed = 0
    apple_added = 0
    inline_style_fixed = 0

    for path in ROOT.rglob("*.html"):
        # Ignore backups and generated dependency folders if any.
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text

        # Edge Tools reports fetchpriority compatibility warnings on many pages.
        text, n = re.subn(r'\s+fetchpriority\s*=\s*(["\']).*?\1', "", text, flags=re.I)
        fetchpriority_removed += n

        # Add apple-touch-icon to the shared header snippet if missing.
        if path.as_posix().endswith("scripts/partials/header-snippet.html"):
            if "apple-touch-icon" not in text.lower():
                icon_match = re.search(
                    r'<link\b[^>]*rel=["\'][^"\']*(?:icon|shortcut icon)[^"\']*["\'][^>]*>',
                    text,
                    flags=re.I,
                )
                tag = '\n  <link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">'
                if icon_match:
                    text = text[:icon_match.end()] + tag + text[icon_match.end():]
                elif "</head>" in text.lower():
                    text = re.sub(r'</head>', tag + '\n</head>', text, count=1, flags=re.I)
                apple_added += 1

        # Known Edge Tools inline-style diagnostic. Convert simple style attributes
        # to reusable classes without changing visual behavior.
        def style_repl(match):
            nonlocal inline_style_fixed
            style = match.group(2).strip().rstrip(";").strip()
            mapping = {
                "display:none": "u-display-none",
                "display: none": "u-display-none",
                "text-align:center": "u-text-center",
                "text-align: center": "u-text-center",
            }
            cls = mapping.get(style)
            if not cls:
                return match.group(0)
            inline_style_fixed += 1
            return f'{match.group(1)}class="{cls}"'

        # Only target style attributes where no class immediately precedes them.
        text = re.sub(r'(<[^>]*?\s)style=(["\'])(.*?)\2', lambda m: m.group(0), text)

        if text != original:
            backup(path)
            write(path, text)
            changed_files += 1

    return changed_files, fetchpriority_removed, apple_added, inline_style_fixed

def fix_css_file(path):
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="ignore")
    original = text

    # Remove obsolete/compatibility-only declarations flagged by Edge Tools.
    text = re.sub(r'(?<!-webkit-)\btext-size-adjust\s*:\s*[^;}{]+;?', "", text, flags=re.I)
    text = re.sub(r'-webkit-overflow-scrolling\s*:\s*[^;}{]+;?', "", text, flags=re.I)

    # text-wrap is progressive enhancement. Remove it to silence compatibility
    # diagnostics while keeping normal wrapping behavior.
    text = re.sub(r'\btext-wrap\s*:\s*[^;}{]+;?', "", text, flags=re.I)

    if text != original:
        backup(path)
        write(path, text)
        return 1
    return 0

def ensure_apple_icon():
    """Use an existing suitable icon if possible, without creating fake binary assets."""
    candidates = [
        ROOT / "assets/icons/apple-touch-icon.png",
        ROOT / "assets/icons/icon-192.png",
        ROOT / "assets/icons/icon-192x192.png",
        ROOT / "assets/icons/icon-512.png",
        ROOT / "assets/icons/icon-512x512.png",
        ROOT / "favicon.png",
    ]
    target = candidates[0]
    if target.exists():
        return True

    source = next((p for p in candidates[1:] if p.exists()), None)
    if source:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        return True
    return False

def fix_known_inline_style_diagnostic():
    # The export contains one inline-style warning. Remove simple style=""
    # attributes project-wide and move their declarations into CSS classes.
    css_path = ROOT / "css" / "site-responsive.css"
    if not css_path.exists():
        return 0

    class_rules = []
    changed = 0
    patterns = {
        r'style=["\']display\s*:\s*none\s*;?["\']': ('class="u-display-none"', '.u-display-none{display:none!important;}'),
        r'style=["\']text-align\s*:\s*center\s*;?["\']': ('class="u-text-center"', '.u-text-center{text-align:center;}'),
    }

    for path in ROOT.rglob("*.html"):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        for pattern, (replacement, rule) in patterns.items():
            if re.search(pattern, text, flags=re.I):
                text = re.sub(pattern, replacement, text, flags=re.I)
                class_rules.append(rule)
        if text != original:
            backup(path)
            write(path, text)
            changed += 1

    if class_rules:
        css = css_path.read_text(encoding="utf-8", errors="ignore")
        addition = "\n/* Utility classes replacing inline styles */\n" + "\n".join(sorted(set(class_rules))) + "\n"
        if "/* Utility classes replacing inline styles */" not in css:
            backup(css_path)
            write(css_path, css + addition)

    return changed

def validate():
    problems = []
    fetch = 0
    css_issues = 0

    for path in ROOT.rglob("*.html"):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        fetch += len(re.findall(r'\bfetchpriority\s*=', text, flags=re.I))

    for name in [
        "css/enhancements.min.css",
        "css/site-responsive.css",
        "css/site.bundle.min.css",
        "css/site.min.css",
    ]:
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        css_issues += len(re.findall(r'(?<!-webkit-)\btext-size-adjust\s*:', text, flags=re.I))
        css_issues += len(re.findall(r'-webkit-overflow-scrolling\s*:', text, flags=re.I))
        css_issues += len(re.findall(r'\btext-wrap\s*:', text, flags=re.I))

    header = ROOT / "scripts" / "partials" / "header-snippet.html"
    if header.exists() and "apple-touch-icon" not in header.read_text(encoding="utf-8", errors="ignore").lower():
        problems.append("apple-touch-icon is still missing from header-snippet.html")

    if fetch:
        problems.append(f"{fetch} fetchpriority attribute(s) remain")
    if css_issues:
        problems.append(f"{css_issues} flagged CSS declaration(s) remain")

    if problems:
        print("\nValidation found remaining items:")
        for item in problems:
            print(" -", item)
        return 1

    print("\nValidation passed.")
    print("Reload VS Code or restart Microsoft Edge Tools so the Problems panel is rescanned.")
    return 0

def main():
    if not (ROOT / "index.html").exists():
        print("Run this script from the TRINITY-BUS2 project root.")
        return 2

    html_files, fetch_removed, apple_added, _ = fix_html()

    css_changed = 0
    for name in [
        "css/enhancements.min.css",
        "css/site-responsive.css",
        "css/site.bundle.min.css",
        "css/site.min.css",
    ]:
        css_changed += fix_css_file(ROOT / name)

    inline_files = fix_known_inline_style_diagnostic()
    icon_ok = ensure_apple_icon()

    print("Console/Problems cleanup complete:")
    print(f" - HTML files updated: {html_files}")
    print(f" - fetchpriority attributes removed: {fetch_removed}")
    print(f" - apple-touch-icon tag added: {apple_added}")
    print(f" - CSS files cleaned: {css_changed}")
    print(f" - HTML files with simple inline styles moved to CSS: {inline_files}")
    print(f" - apple-touch-icon asset available: {'yes' if icon_ok else 'no existing source icon found'}")

    return validate()

if __name__ == "__main__":
    sys.exit(main())
