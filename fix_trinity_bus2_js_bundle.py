from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path.cwd()
JS = ROOT / "js"

UTILS = JS / "utils.js"
ENHANCEMENTS = JS / "site-enhancements.js"
APP = JS / "app.min.js"
BUNDLE = JS / "site.bundle.min.js"

def read(path):
    return path.read_text(encoding="utf-8", errors="strict").strip()

def main():
    required = [UTILS, ENHANCEMENTS, APP]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]

    if missing:
        print("Run this file from the TRINITY-BUS2 project root.")
        print("Missing:", ", ".join(missing))
        return 2

    utils = read(UTILS)
    enhancements = read(ENHANCEMENTS)
    app = read(APP)

    # Rebuild the corrupted bundle from the clean source files.
    bundle = (
        "/* Trinity Bus Express production bundle. Rebuilt from valid source files. */\n"
        + utils + "\n"
        + enhancements + "\n"
        + app + "\n"
    )

    BUNDLE.write_text(bundle, encoding="utf-8", newline="\n")

    print("Rebuilt js/site.bundle.min.js")
    print(f"Bundle size: {BUNDLE.stat().st_size} bytes")

    # Optional real JavaScript syntax check when Node.js is installed.
    node = shutil.which("node")
    if node:
        result = subprocess.run(
            [node, "--check", str(BUNDLE)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("\nJavaScript syntax validation FAILED:")
            print(result.stderr.strip())
            return 1

        print("Node.js syntax check: passed")
    else:
        print("Node.js not installed, skipped Node syntax check.")

    # Basic checks for the exact corruption seen in the old file.
    rebuilt = BUNDLE.read_text(encoding="utf-8")

    bad_fragments = [
        'whatsapp:"https: (()=>',
        'href="https: nav.appendChild',
        'footer.innerHTML=`<a class="mobile-menu-cta" href="${prefix}booking.html">Book Seat</a><a class="mobile-menu-whatsapp" href="https:'
    ]

    found = [fragment for fragment in bad_fragments if fragment in rebuilt]

    if found:
        print("\nValidation FAILED. Corrupt fragments remain.")
        return 1

    if "https://wa.me/254754932823" not in rebuilt:
        print("\nValidation FAILED. WhatsApp URL is missing.")
        return 1

    if "window.TBE=" not in rebuilt:
        print("\nValidation FAILED. TBE helper is missing.")
        return 1

    print("\nValidation passed.")
    print("Reload VS Code with Developer: Reload Window, then open Problems with Ctrl+Shift+M.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
