from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path.cwd()
JS = ROOT / "js"

SOURCES = [
    JS / "utils.js",
    JS / "site-enhancements.js",
    JS / "app.min.js",
]
BUNDLE = JS / "site.bundle.min.js"

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict").strip()

def main():
    if not (ROOT / "index.html").exists():
        print("Run this script from the TRINITY-BUS2 project root.")
        return 2

    missing = [str(p.relative_to(ROOT)) for p in SOURCES if not p.exists()]
    if missing:
        print("Missing source file(s):")
        for item in missing:
            print(" -", item)
        return 2

    parts = [read(path) for path in SOURCES]

    # Rebuild from clean source files only.
    # The old corrupted bundle is never reused.
    rebuilt = (
        "/* Trinity Bus Express production bundle */\n"
        + "\n".join(parts)
        + "\n"
    )

    # Sanity checks against the corruption previously seen.
    checks = [
        ("TBE helper", 'window.TBE='),
        ("WhatsApp URL", 'https://wa.me/254754932823'),
        ("DOMContentLoaded", 'DOMContentLoaded'),
    ]
    missing_checks = [name for name, token in checks if token not in rebuilt]

    if missing_checks:
        print("Rebuild validation failed. Missing:")
        for name in missing_checks:
            print(" -", name)
        return 1

    # Detect only truly broken fragments, not valid https:// URLs.
    bad_fragments = [
        'whatsapp:"https: (()=>',
        'href="https: nav.appendChild',
        'href="https: footer',
        'footer.innerHTML=`<a class="mobile-menu-cta" href="${prefix}booking.html">Book Seat</a><a class="mobile-menu-whatsapp" href="https: nav.appendChild',
    ]

    found = [frag for frag in bad_fragments if frag in rebuilt]
    if found:
        print("Rebuild validation failed. Corrupt fragment(s) still found:")
        for frag in found:
            print(" -", frag)
        return 1

    # Replace the bundle atomically.
    temp = BUNDLE.with_suffix(".min.js.tmp")
    temp.write_text(rebuilt, encoding="utf-8", newline="\n")
    temp.replace(BUNDLE)

    print("Rebuilt js/site.bundle.min.js from clean source files.")
    print(f"Bundle size: {BUNDLE.stat().st_size} bytes")

    # Use Node.js syntax validation when available.
    node = shutil.which("node")
    if node:
        result = subprocess.run(
            [node, "--check", str(BUNDLE)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("\nNode.js syntax validation FAILED:")
            print(result.stderr.strip())
            return 1
        print("Node.js syntax check: passed")
    else:
        print("Node.js not installed, skipped Node syntax check.")

    # Final integrity check.
    final_text = read(BUNDLE)
    if final_text != rebuilt.strip():
        print("\nValidation FAILED. Written bundle does not match rebuilt content.")
        return 1

    print("\nValidation passed.")
    print("Now reload VS Code: Ctrl+Shift+P, then Developer: Reload Window.")
    print("Open Problems with Ctrl+Shift+M.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
