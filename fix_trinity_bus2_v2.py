from pathlib import Path
import re
import sys

ROOT = Path.cwd()
LIVE_BASE = "https://victor-kibet-cybersecurity-guy.github.io/trinity-bus2"

ROUTE_DATA = '''window.TBE_ROUTES = [
  { slug: "nairobi-to-kampala", origin: "Nairobi", destination: "Kampala", country: "Uganda", flag: "🇺🇬", fare: 3500, duration: "12–14 hours", departure: "6:00 PM (Daily)", arrival: "7:00 AM next day", border: "Busia / Malaba OSBP", terminal: "River Road Terminal, Nairobi", stopovers: "Nakuru, Eldoret, Malaba, Jinja", bus: "Executive Luxury Coach" },
  { slug: "nairobi-to-kigali", origin: "Nairobi", destination: "Kigali", country: "Rwanda", flag: "🇷🇼", fare: 5500, duration: "18–20 hours", departure: "4:00 PM (Daily)", arrival: "11:00 AM next day", border: "Gatuna / Katuna OSBP", terminal: "River Road Terminal, Nairobi", stopovers: "Nakuru, Eldoret, Kampala, Gatuna", bus: "Executive Luxury Coach" },
  { slug: "nairobi-to-juba", origin: "Nairobi", destination: "Juba", country: "South Sudan", flag: "🇸🇸", fare: 7000, duration: "22–26 hours", departure: "2:00 PM (Mon, Wed, Sat)", arrival: "3:00 PM next day", border: "Nimule / Elegu Checkpoint", terminal: "Accra Road Terminal, Nairobi", stopovers: "Eldoret, Kampala, Gulu, Nimule", bus: "Cross-Border Express Coach" },
  { slug: "nairobi-to-goma", origin: "Nairobi", destination: "Goma", country: "DRC", flag: "🇨🇩", fare: 7500, duration: "24–28 hours", departure: "1:00 PM (Tue, Fri)", arrival: "5:00 PM next day", border: "Grande Barrière / Gisenyi", terminal: "Accra Road Terminal, Nairobi", stopovers: "Eldoret, Kampala, Kabale, Gisenyi", bus: "Cross-Border Express Coach" },
  { slug: "nairobi-to-bujumbura", origin: "Nairobi", destination: "Bujumbura", country: "Burundi", flag: "🇧🇮", fare: 7000, duration: "22–25 hours", departure: "3:00 PM (Wed, Sun)", arrival: "3:00 PM next day", border: "Kanyaru / Akanyaru Border", terminal: "River Road Terminal, Nairobi", stopovers: "Eldoret, Kampala, Kigali", bus: "Executive Luxury Coach" },
  { slug: "kampala-to-nairobi", origin: "Kampala", destination: "Nairobi", country: "Kenya", flag: "🇰🇪", fare: 3500, duration: "12–14 hours", departure: "6:00 PM (Daily)", arrival: "7:00 AM next day", border: "Malaba / Busia OSBP", terminal: "Bakuli Terminal, Sir Apollo Kaggwa Rd, Kampala", stopovers: "Jinja, Malaba, Eldoret, Nakuru", bus: "Executive Luxury Coach" },
  { slug: "kampala-to-kigali", origin: "Kampala", destination: "Kigali", country: "Rwanda", flag: "🇷🇼", fare: 2500, duration: "8–10 hours", departure: "8:00 PM (Daily)", arrival: "6:00 AM next day", border: "Gatuna OSBP", terminal: "Bakuli Terminal, Kampala", stopovers: "Masaka, Mbarara, Gatuna", bus: "Comfort Express Coach" },
  { slug: "kigali-to-nairobi", origin: "Kigali", destination: "Nairobi", country: "Kenya", flag: "🇰🇪", fare: 5500, duration: "18–20 hours", departure: "3:00 PM (Daily)", arrival: "10:00 AM next day", border: "Gatuna OSBP", terminal: "Nyabugogo Bus Park, Kigali", stopovers: "Gatuna, Kampala, Eldoret, Nakuru", bus: "Executive Luxury Coach" }
];
'''

def read(path):
    return path.read_text(encoding="utf-8")

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def backup(path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            bak.write_bytes(path.read_bytes())

def replace_route_array(text):
    pattern = r'const\s+ROUTES\s*=\s*\[\s*.*?\n\];'
    replacement = 'const ROUTES = window.TBE_ROUTES || [];'
    new, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    return new, count

def ensure_script_before(html, target_src, required_src):
    if f'src="{required_src}"' in html:
        return html
    marker = f'<script src="{target_src}" defer></script>'
    if marker in html:
        return html.replace(marker, f'<script src="{required_src}" defer></script>\n{marker}', 1)
    return html

def remove_footer_wa_artifact(text):
    pos = text.lower().find("</footer>")
    if pos < 0:
        return text, 0
    before = text[:pos + len("</footer>")]
    after = text[pos + len("</footer>"):]
    original = after
    after = re.sub(r'<a\b[^>]*>\s*WA\s*</a>', '', after, flags=re.I | re.S)
    after = re.sub(r'<(?:span|div|button)\b[^>]*>\s*WA\s*</(?:span|div|button)>', '', after, flags=re.I | re.S)
    after = re.sub(r'(?<=>)\s*WA\s*(?=<)', '', after, flags=re.I)
    return before + after, int(after != original)

def fix_all_footer_artifacts():
    changed = 0
    for path in ROOT.rglob("*.html"):
        backup(path)
        text = read(path)
        fixed, did = remove_footer_wa_artifact(text)
        if did:
            write(path, fixed)
            changed += 1
    return f"Footer WA artifact removed from {changed} HTML file(s)"

def create_shared_route_data():
    path = ROOT / "js" / "route-data.js"
    if path.exists():
        backup(path)
    write(path, ROUTE_DATA + "\n")
    return "Created js/route-data.js as the single shared route source"

def fix_routes_js():
    path = ROOT / "js" / "routes.js"
    if not path.exists():
        return "js/routes.js missing"
    backup(path)
    text = read(path)

    text, count = replace_route_array(text)
    if count != 1 and "window.TBE_ROUTES" not in text:
        return "Could not safely replace duplicated ROUTES array in js/routes.js"

    if "function bookingUrl(" not in text:
        marker = "function renderRoutes(data = ROUTES) {"
        helper = '''function bookingUrl(route) {
  const current = new URLSearchParams(window.location.search);
  const next = new URLSearchParams({ route: route.slug });
  const date = current.get("date");
  const passengers = current.get("passengers");
  if (date) next.set("date", date);
  if (passengers) next.set("passengers", passengers);
  return `booking.html?${next.toString()}`;
}

'''
        text = text.replace(marker, helper + marker, 1)

    text = text.replace('href="booking.html?route=${r.slug}"', 'href="${bookingUrl(r)}"')

    old_dom = re.compile(
        r'document\.addEventListener\("DOMContentLoaded",\s*\(\)\s*=>\s*\{\s*'
        r'renderRoutes\(\);\s*'
        r'\["routeSearch",\s*"countryFilter",\s*"routeSort"\]\.forEach\(id\s*=>\s*\{\s*'
        r'document\.getElementById\(id\)\?\.addEventListener\("input",\s*\(\)\s*=>\s*renderRoutes\(filter\(\)\)\);\s*'
        r'\}\);\s*'
        r'\}\);',
        flags=re.S
    )

    new_dom = '''document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const origin = (params.get("origin") || "").trim().toLowerCase();
  const destination = (params.get("destination") || "").trim().toLowerCase();

  let initialRoutes = ROUTES;

  if (origin || destination) {
    initialRoutes = ROUTES.filter(route => {
      const originMatch = !origin || route.origin.toLowerCase() === origin;
      const destinationMatch = !destination || route.destination.toLowerCase() === destination;
      return originMatch && destinationMatch;
    });

    const searchInput = document.getElementById("routeSearch");
    if (searchInput) {
      searchInput.value = [params.get("origin"), params.get("destination")]
        .filter(Boolean)
        .join(" → ");
    }
  }

  renderRoutes(initialRoutes);

  ["routeSearch", "countryFilter", "routeSort"].forEach(id => {
    document.getElementById(id)?.addEventListener("input", () => renderRoutes(filter()));
    document.getElementById(id)?.addEventListener("change", () => renderRoutes(filter()));
  });
});'''

    text, dom_count = old_dom.subn(new_dom, text, count=1)
    if dom_count == 0 and 'params.get("origin")' not in text:
        return "Could not safely update routes page query handling"

    write(path, text)
    return "js/routes.js fixed"

def fix_booking_js():
    path = ROOT / "js" / "booking.js"
    if not path.exists():
        return "js/booking.js missing"
    backup(path)
    text = read(path)

    text, count = replace_route_array(text)
    if count != 1 and "window.TBE_ROUTES" not in text:
        return "Could not safely replace duplicated ROUTES array in js/booking.js"

    if "function localDateISO(" not in text:
        marker = 'document.addEventListener("DOMContentLoaded", () => {'
        helper = '''function localDateISO(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

'''
        text = text.replace(marker, helper + marker, 1)

    date_pattern = re.compile(
        r'// Check URL query parameters\s*'
        r'const urlParams = new URLSearchParams\(window\.location\.search\);\s*'
        r'const routeParam = urlParams\.get\("route"\);\s*'
        r'if \(routeParam && ROUTES\.some\(r => r\.slug === routeParam\)\) \{\s*'
        r'routeSel\.value = routeParam;\s*'
        r'\}\s*'
        r'// Pre-fill Date if not set\s*'
        r'const dateInput = document\.getElementById\("date"\);\s*'
        r'if \(dateInput && !dateInput\.value\) \{\s*'
        r'const tomorrow = new Date\(\);\s*'
        r'tomorrow\.setDate\(tomorrow\.getDate\(\) \+ 1\);\s*'
        r'dateInput\.value = tomorrow\.toISOString\(\)\.split\("T"\)\[0\];\s*'
        r'dateInput\.min = new Date\(\)\.toISOString\(\)\.split\("T"\)\[0\];\s*'
        r'\}',
        flags=re.S
    )

    replacement = '''// Read route search values passed from the homepage/routes page.
  const urlParams = new URLSearchParams(window.location.search);

  const routeParam = urlParams.get("route");
  if (routeParam && ROUTES.some(r => r.slug === routeParam)) {
    routeSel.value = routeParam;
  }

  const passengerInput = document.getElementById("passengers");
  const passengerParam = Number.parseInt(urlParams.get("passengers"), 10);
  if (passengerInput && Number.isInteger(passengerParam) && passengerParam >= 1 && passengerParam <= 5) {
    passengerInput.value = String(passengerParam);
  }

  const dateInput = document.getElementById("date");
  if (dateInput) {
    const today = localDateISO();
    dateInput.min = today;

    const requestedDate = urlParams.get("date");
    if (requestedDate && /^\\d{4}-\\d{2}-\\d{2}$/.test(requestedDate) && requestedDate >= today) {
      dateInput.value = requestedDate;
    } else if (!dateInput.value) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      dateInput.value = localDateISO(tomorrow);
    }
  }'''

    text, changed = date_pattern.subn(replacement, text, count=1)
    if changed == 0 and 'urlParams.get("passengers")' not in text:
        return "Could not safely replace booking date/query setup"

    write(path, text)
    return "js/booking.js fixed"

def fix_script_order():
    results = []
    for filename, target in [("routes.html", "js/routes.js"), ("booking.html", "js/booking.js")]:
        path = ROOT / filename
        if not path.exists():
            results.append(f"{filename} missing")
            continue

        backup(path)
        html = read(path)

        route_tag = '<script src="js/route-data.js" defer></script>'
        utils_tag = '<script src="js/utils.js" defer></script>'
        target_tag = f'<script src="{target}" defer></script>'

        if target_tag in html:
            html = html.replace(route_tag, "")
            html = html.replace(utils_tag, "")
            html = html.replace(target_tag, route_tag + "\n" + utils_tag + "\n" + target_tag, 1)

        write(path, html)
        results.append(f"{filename} dependency order fixed")

    return "; ".join(results)

def fix_404():
    path = ROOT / "404.html"
    if not path.exists():
        return "404.html missing"
    backup(path)
    text = read(path)
    text = re.sub(
        r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
        '<meta name="robots" content="noindex,follow">',
        text,
        count=1,
        flags=re.I
    )
    write(path, text)
    return "404.html set to noindex,follow"

def fix_robots():
    path = ROOT / "robots.txt"
    if path.exists():
        backup(path)
    write(path,
          "User-agent: *\n"
          "Allow: /\n\n"
          f"Sitemap: {LIVE_BASE}/sitemap.xml\n"
          f"Sitemap: {LIVE_BASE}/image-sitemap.xml\n")
    return "robots.txt corrected"

def fix_sitemaps():
    changed = []
    for name in ("sitemap.xml", "image-sitemap.xml"):
        path = ROOT / name
        if not path.exists():
            continue
        backup(path)
        text = read(path)
        text = text.replace("https://example.com/trinity-bus-express", LIVE_BASE)
        text = text.replace("https://trinitybusexpress.com", LIVE_BASE)

        if name == "sitemap.xml":
            lines = [
                line for line in text.splitlines()
                if not re.search(r"<loc>[^<]*/404\.html</loc>", line, flags=re.I)
            ]
            text = "\n".join(lines).rstrip() + "\n"

        write(path, text)
        changed.append(name)
    return "Corrected sitemap hosts: " + ", ".join(changed)

def validate():
    errors = []

    route_data = ROOT / "js" / "route-data.js"
    if not route_data.exists() or "🇸🇸" not in read(route_data):
        errors.append("shared route data or South Sudan flag is missing")

    routes_js = ROOT / "js" / "routes.js"
    if routes_js.exists():
        t = read(routes_js)
        if "🇸SS" in t:
            errors.append("old South Sudan typo remains in routes.js")
        if "bookingUrl(route)" not in t:
            errors.append("routes.js booking parameter preservation is missing")
        if 'params.get("origin")' not in t or 'params.get("destination")' not in t:
            errors.append("routes.js homepage parameter handling is missing")

    booking_js = ROOT / "js" / "booking.js"
    if booking_js.exists():
        t = read(booking_js)
        if ".toISOString().split(" in t:
            errors.append("booking.js still contains UTC ISO date construction")
        if "localDateISO" not in t:
            errors.append("booking.js local-date helper is missing")
        if 'urlParams.get("passengers")' not in t:
            errors.append("booking passenger prefill is missing")

    for page, target in [("routes.html", "js/routes.js"), ("booking.html", "js/booking.js")]:
        path = ROOT / page
        if path.exists():
            t = read(path)
            positions = [
                t.find('src="js/route-data.js"'),
                t.find('src="js/utils.js"'),
                t.find(f'src="{target}"')
            ]
            if min(positions) < 0 or positions != sorted(positions):
                errors.append(f"{page} script dependency order is wrong")

    page404 = ROOT / "404.html"
    if page404.exists() and "noindex,follow" not in read(page404).replace(" ", "").lower():
        errors.append("404 page is still indexable")

    robots = ROOT / "robots.txt"
    if robots.exists() and "example.com" in read(robots):
        errors.append("robots.txt still uses example.com")

    if errors:
        print("\nVALIDATION FAILED")
        for err in errors:
            print(" -", err)
        return 1

    print("\nValidation passed.")
    return 0

def main():
    required = ["index.html", "routes.html", "booking.html", "404.html", "js/routes.js", "js/booking.js"]
    missing = [name for name in required if not (ROOT / name).exists()]
    if missing:
        print("Run this file from the TRINITY-BUS2 project root.")
        print("Missing:", ", ".join(missing))
        return 2

    results = [
        fix_all_footer_artifacts(),
        create_shared_route_data(),
        fix_routes_js(),
        fix_booking_js(),
        fix_script_order(),
        fix_404(),
        fix_robots(),
        fix_sitemaps(),
    ]

    print("Trinity Bus Express v2 repair:")
    for result in results:
        print(" -", result)

    return validate()

if __name__ == "__main__":
    sys.exit(main())
