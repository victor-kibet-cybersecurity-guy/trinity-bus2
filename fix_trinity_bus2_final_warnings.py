from pathlib import Path
import json
import re
import sys

ROOT = Path.cwd()

INDEX = ROOT / "index.html"
HINTRC = ROOT / ".hintrc"

def read(path):
    return path.read_text(encoding="utf-8", errors="ignore")

def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

def remove_fetchpriority():
    if not INDEX.exists():
        return 0

    text = read(INDEX)
    new_text, count = re.subn(
        r'\s+fetchpriority\s*=\s*(["\'])high\1',
        '',
        text,
        flags=re.I
    )

    if count:
        write(INDEX, new_text)

    return count

def configure_webhint_ignore():
    """
    Ignore only the apple-touch-icons hint for the HTML partial.
    The partial is not a standalone page, but Edge Tools/Webhint scans it as one.
    """
    ignore_entry = {
        "domain": "scripts/partials/header-snippet.html",
        "hints": ["apple-touch-icons"]
    }

    if HINTRC.exists():
        raw = read(HINTRC).strip()

        try:
            config = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            # Preserve an invalid existing file instead of overwriting it.
            fallback = ROOT / ".hintrc.apple-touch-fix.json"
            write(
                fallback,
                json.dumps({"ignoredUrls": [ignore_entry]}, indent=2) + "\n"
            )
            return (
                False,
                ".hintrc is not valid JSON. Created .hintrc.apple-touch-fix.json "
                "instead so your existing config was not destroyed."
            )
    else:
        config = {}

    ignored = config.get("ignoredUrls")
    if not isinstance(ignored, list):
        ignored = []

    found = False
    for item in ignored:
        if not isinstance(item, dict):
            continue
        if item.get("domain") == ignore_entry["domain"]:
            hints = item.get("hints")
            if not isinstance(hints, list):
                hints = []
            if "apple-touch-icons" not in hints and "*" not in hints:
                hints.append("apple-touch-icons")
            item["hints"] = hints
            found = True
            break

    if not found:
        ignored.append(ignore_entry)

    config["ignoredUrls"] = ignored
    write(HINTRC, json.dumps(config, indent=2) + "\n")
    return True, ".hintrc configured to ignore the false positive on header-snippet.html"

def delete_bak_files():
    deleted = []
    failed = []

    # Delete .bak and variants created by earlier repair scripts.
    patterns = ["*.bak", "*.bak.*", "*.lcp.bak", "*.console-fix.bak"]

    seen = set()
    for pattern in patterns:
        for path in ROOT.rglob(pattern):
            if not path.is_file():
                continue

            resolved = str(path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)

            try:
                path.unlink()
                deleted.append(path.relative_to(ROOT).as_posix())
            except Exception as exc:
                failed.append((path.relative_to(ROOT).as_posix(), str(exc)))

    return deleted, failed

def validate():
    problems = []

    if INDEX.exists() and re.search(
        r'\bfetchpriority\s*=\s*(["\'])high\1',
        read(INDEX),
        flags=re.I
    ):
        problems.append("index.html still contains fetchpriority=high")

    if HINTRC.exists():
        try:
            config = json.loads(read(HINTRC))
            ignored = config.get("ignoredUrls", [])
            matched = any(
                isinstance(item, dict)
                and item.get("domain") == "scripts/partials/header-snippet.html"
                and (
                    "apple-touch-icons" in item.get("hints", [])
                    or "*" in item.get("hints", [])
                )
                for item in ignored
            )
            if not matched:
                problems.append(".hintrc does not ignore apple-touch-icons for the partial")
        except Exception:
            problems.append(".hintrc could not be validated")
    else:
        problems.append(".hintrc was not created")

    bak_left = [
        p for p in ROOT.rglob("*")
        if p.is_file() and (
            p.name.endswith(".bak")
            or ".bak." in p.name
            or p.name.endswith(".lcp.bak")
            or p.name.endswith(".console-fix.bak")
        )
    ]
    if bak_left:
        problems.append(f"{len(bak_left)} backup file(s) remain")

    if problems:
        print("\nVALIDATION FAILED")
        for problem in problems:
            print(" -", problem)
        return 1

    print("\nValidation passed.")
    print("Reload VS Code so Microsoft Edge Tools/Webhint rescans the project.")
    return 0

def main():
    if not (ROOT / "index.html").exists():
        print("Run this file from the TRINITY-BUS2 project root.")
        return 2

    fetch_count = remove_fetchpriority()
    hintrc_ok, hintrc_message = configure_webhint_ignore()
    deleted, failed = delete_bak_files()

    print("Trinity Bus Express final Problems cleanup:")
    print(f" - fetchpriority attributes removed from index.html: {fetch_count}")
    print(f" - {hintrc_message}")
    print(f" - backup files deleted: {len(deleted)}")

    if failed:
        print(f" - backup files that could not be deleted: {len(failed)}")
        for name, error in failed:
            print(f"   {name}: {error}")

    if not hintrc_ok:
        print("\nThe existing .hintrc needs manual review before the Apple-touch warning can be suppressed safely.")
        return 1

    return validate()

if __name__ == "__main__":
    sys.exit(main())
