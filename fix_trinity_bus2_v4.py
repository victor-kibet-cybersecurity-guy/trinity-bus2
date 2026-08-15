from pathlib import Path
import re
import sys

ROOT = Path.cwd()

ROUTE_CARDS = '''<div id="routeResults" class="grid-2">
          <article class="card route-card" data-route-card data-slug="nairobi-to-kampala" data-origin="nairobi" data-destination="kampala" data-country="uganda" data-fare="3500" data-duration="12">
            <div class="route-card-top"><span class="pill">🇺🇬 Uganda</span><button class="favorite" data-slug="nairobi-to-kampala" aria-label="Favorite Nairobi to Kampala route">♡</button></div>
            <h3>Nairobi → Kampala</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 6:00 PM (Daily)</p>
              <p>⏳ <strong>Est. Duration:</strong> 12–14 hours</p>
              <p>🛂 <strong>Border Post:</strong> Busia / Malaba OSBP</p>
              <p>📍 <strong>Key Stops:</strong> Nakuru, Eldoret, Malaba, Jinja</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 3,500</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="nairobi-to-kampala" href="booking.html?route=nairobi-to-kampala">Request Seat</a><a class="btn btn-outline" href="routes/nairobi-to-kampala.html">Guide</a></div></div>
          </article>

          <article class="card route-card" data-route-card data-slug="nairobi-to-kigali" data-origin="nairobi" data-destination="kigali" data-country="rwanda" data-fare="5500" data-duration="18">
            <div class="route-card-top"><span class="pill">🇷🇼 Rwanda</span><button class="favorite" data-slug="nairobi-to-kigali" aria-label="Favorite Nairobi to Kigali route">♡</button></div>
            <h3>Nairobi → Kigali</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 4:00 PM (Daily)</p>
              <p>⏳ <strong>Est. Duration:</strong> 18–20 hours</p>
              <p>🛂 <strong>Border Post:</strong> Gatuna / Katuna OSBP</p>
              <p>📍 <strong>Key Stops:</strong> Nakuru, Eldoret, Kampala, Gatuna</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 5,500</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="nairobi-to-kigali" href="booking.html?route=nairobi-to-kigali">Request Seat</a><a class="btn btn-outline" href="routes/nairobi-to-kigali.html">Guide</a></div></div>
          </article>

          <article class="card route-card" data-route-card data-slug="nairobi-to-juba" data-origin="nairobi" data-destination="juba" data-country="south sudan" data-fare="7000" data-duration="22">
            <div class="route-card-top"><span class="pill">🇸🇸 South Sudan</span><button class="favorite" data-slug="nairobi-to-juba" aria-label="Favorite Nairobi to Juba route">♡</button></div>
            <h3>Nairobi → Juba</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 2:00 PM (Mon, Wed, Sat)</p>
              <p>⏳ <strong>Est. Duration:</strong> 22–26 hours</p>
              <p>🛂 <strong>Border Post:</strong> Nimule / Elegu Checkpoint</p>
              <p>📍 <strong>Key Stops:</strong> Eldoret, Kampala, Gulu, Nimule</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 7,000</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="nairobi-to-juba" href="booking.html?route=nairobi-to-juba">Request Seat</a><a class="btn btn-outline" href="routes/nairobi-to-juba.html">Guide</a></div></div>
          </article>

          <article class="card route-card" data-route-card data-slug="nairobi-to-goma" data-origin="nairobi" data-destination="goma" data-country="drc" data-fare="7500" data-duration="24">
            <div class="route-card-top"><span class="pill">🇨🇩 DRC</span><button class="favorite" data-slug="nairobi-to-goma" aria-label="Favorite Nairobi to Goma route">♡</button></div>
            <h3>Nairobi → Goma</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 1:00 PM (Tue, Fri)</p>
              <p>⏳ <strong>Est. Duration:</strong> 24–28 hours</p>
              <p>🛂 <strong>Border Post:</strong> Grande Barrière / Gisenyi</p>
              <p>📍 <strong>Key Stops:</strong> Eldoret, Kampala, Kabale, Gisenyi</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 7,500</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="nairobi-to-goma" href="booking.html?route=nairobi-to-goma">Request Seat</a><a class="btn btn-outline" href="routes/nairobi-to-goma.html">Guide</a></div></div>
          </article>

          <article class="card route-card" data-route-card data-slug="nairobi-to-bujumbura" data-origin="nairobi" data-destination="bujumbura" data-country="burundi" data-fare="7000" data-duration="22">
            <div class="route-card-top"><span class="pill">🇧🇮 Burundi</span><button class="favorite" data-slug="nairobi-to-bujumbura" aria-label="Favorite Nairobi to Bujumbura route">♡</button></div>
            <h3>Nairobi → Bujumbura</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 3:00 PM (Wed, Sun)</p>
              <p>⏳ <strong>Est. Duration:</strong> 22–25 hours</p>
              <p>🛂 <strong>Border Post:</strong> Kanyaru / Akanyaru Border</p>
              <p>📍 <strong>Key Stops:</strong> Eldoret, Kampala, Kigali</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 7,000</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="nairobi-to-bujumbura" href="booking.html?route=nairobi-to-bujumbura">Request Seat</a><a class="btn btn-outline" href="routes/nairobi-to-bujumbura.html">Guide</a></div></div>
          </article>

          <article class="card route-card" data-route-card data-slug="kampala-to-nairobi" data-origin="kampala" data-destination="nairobi" data-country="kenya" data-fare="3500" data-duration="12">
            <div class="route-card-top"><span class="pill">🇰🇪 Kenya</span><button class="favorite" data-slug="kampala-to-nairobi" aria-label="Favorite Kampala to Nairobi route">♡</button></div>
            <h3>Kampala → Nairobi</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 6:00 PM (Daily)</p>
              <p>⏳ <strong>Est. Duration:</strong> 12–14 hours</p>
              <p>🛂 <strong>Border Post:</strong> Malaba / Busia OSBP</p>
              <p>📍 <strong>Key Stops:</strong> Jinja, Malaba, Eldoret, Nakuru</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 3,500</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="kampala-to-nairobi" href="booking.html?route=kampala-to-nairobi">Request Seat</a><a class="btn btn-outline" href="routes/kampala-to-nairobi.html">Guide</a></div></div>
          </article>

          <article class="card route-card" data-route-card data-slug="kampala-to-kigali" data-origin="kampala" data-destination="kigali" data-country="rwanda" data-fare="2500" data-duration="8">
            <div class="route-card-top"><span class="pill">🇷🇼 Rwanda</span><button class="favorite" data-slug="kampala-to-kigali" aria-label="Favorite Kampala to Kigali route">♡</button></div>
            <h3>Kampala → Kigali</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 8:00 PM (Daily)</p>
              <p>⏳ <strong>Est. Duration:</strong> 8–10 hours</p>
              <p>🛂 <strong>Border Post:</strong> Gatuna OSBP</p>
              <p>📍 <strong>Key Stops:</strong> Masaka, Mbarara, Gatuna</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 2,500</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="kampala-to-kigali" href="booking.html?route=kampala-to-kigali">Request Seat</a><a class="btn btn-outline" href="routes/kampala-to-kigali.html">Guide</a></div></div>
          </article>

          <article class="card route-card" data-route-card data-slug="kigali-to-nairobi" data-origin="kigali" data-destination="nairobi" data-country="kenya" data-fare="5500" data-duration="18">
            <div class="route-card-top"><span class="pill">🇰🇪 Kenya</span><button class="favorite" data-slug="kigali-to-nairobi" aria-label="Favorite Kigali to Nairobi route">♡</button></div>
            <h3>Kigali → Nairobi</h3>
            <div class="route-meta">
              <p>⏰ <strong>Departure:</strong> 3:00 PM (Daily)</p>
              <p>⏳ <strong>Est. Duration:</strong> 18–20 hours</p>
              <p>🛂 <strong>Border Post:</strong> Gatuna OSBP</p>
              <p>📍 <strong>Key Stops:</strong> Gatuna, Kampala, Eldoret, Nakuru</p>
            </div>
            <div class="route-card-footer"><div><small class="muted">Est. Starting Fare</small><strong class="price">KES 5,500</strong></div><div class="actions"><a class="btn btn-primary route-book-link" data-route="kigali-to-nairobi" href="booking.html?route=kigali-to-nairobi">Request Seat</a><a class="btn btn-outline" href="routes/kigali-to-nairobi.html">Guide</a></div></div>
          </article>
        </div>
        <div id="routeNoResults" class="card" hidden style="text-align:center;padding:40px;margin-top:20px;">
          <h3>No routes matched your search.</h3>
          <p class="muted">Try adjusting your origin, destination, country, or search text.</p>
        </div>'''

ROUTES_JS = '''const ROUTES = window.TBE_ROUTES || [];

const homepageState = {
  origin: "",
  destination: "",
  date: "",
  passengers: ""
};

function bookingUrl(slug) {
  const next = new URLSearchParams({ route: slug });
  if (homepageState.date) next.set("date", homepageState.date);
  if (homepageState.passengers) next.set("passengers", homepageState.passengers);
  return `booking.html?${next.toString()}`;
}

function updateBookingLinks() {
  document.querySelectorAll(".route-book-link[data-route], .comparison-book-link[data-route]").forEach(link => {
    link.href = bookingUrl(link.dataset.route);
  });
}

function bindFavs() {
  const saved = JSON.parse(localStorage.getItem("tbe-favorites") || "[]");

  document.querySelectorAll(".favorite[data-slug]").forEach(button => {
    const slug = button.dataset.slug;
    const isFav = saved.includes(slug);
    button.classList.toggle("active", isFav);
    button.textContent = isFav ? "♥" : "♡";

    button.onclick = () => {
      let favs = JSON.parse(localStorage.getItem("tbe-favorites") || "[]");
      favs = favs.includes(slug) ? favs.filter(item => item !== slug) : [...favs, slug];
      localStorage.setItem("tbe-favorites", JSON.stringify(favs));
      bindFavs();
    };
  });
}

function applyFilters() {
  const query = (document.getElementById("routeSearch")?.value || "").trim().toLowerCase();
  const country = (document.getElementById("countryFilter")?.value || "").trim().toLowerCase();
  const sort = document.getElementById("routeSort")?.value || "";

  const cards = [...document.querySelectorAll("[data-route-card]")];

  cards.forEach(card => {
    const cardText = card.textContent.toLowerCase();
    const originMatch = !homepageState.origin || card.dataset.origin === homepageState.origin;
    const destinationMatch = !homepageState.destination || card.dataset.destination === homepageState.destination;
    const queryMatch = !query || cardText.includes(query);
    const countryMatch = !country || card.dataset.country === country;

    card.hidden = !(originMatch && destinationMatch && queryMatch && countryMatch);
  });

  const visibleCards = cards.filter(card => !card.hidden);

  if (sort === "fare") {
    visibleCards.sort((a, b) => Number(a.dataset.fare) - Number(b.dataset.fare));
  } else if (sort === "duration") {
    visibleCards.sort((a, b) => Number(a.dataset.duration) - Number(b.dataset.duration));
  }

  const container = document.getElementById("routeResults");
  visibleCards.forEach(card => container?.appendChild(card));

  const noResults = document.getElementById("routeNoResults");
  if (noResults) noResults.hidden = visibleCards.length !== 0;
}

document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);

  homepageState.origin = (params.get("origin") || "").trim().toLowerCase();
  homepageState.destination = (params.get("destination") || "").trim().toLowerCase();
  homepageState.date = (params.get("date") || "").trim();
  homepageState.passengers = (params.get("passengers") || "").trim();

  // Keep the free-text search box empty. Homepage origin/destination are tracked separately.
  const routeSearch = document.getElementById("routeSearch");
  if (routeSearch) routeSearch.value = "";

  ["routeSearch", "countryFilter", "routeSort"].forEach(id => {
    document.getElementById(id)?.addEventListener("input", applyFilters);
    document.getElementById(id)?.addEventListener("change", applyFilters);
  });

  updateBookingLinks();
  bindFavs();
  applyFilters();
});
'''

def read(path):
    return path.read_text(encoding="utf-8")

def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

def backup(path):
    bak = path.with_suffix(path.suffix + ".bak")
    if path.exists() and not bak.exists():
        bak.write_bytes(path.read_bytes())

def remove_404_from_html_sitemap():
    path = ROOT / "html-sitemap.html"
    if not path.exists():
        return "html-sitemap.html missing"

    backup(path)
    text = read(path)
    new, count = re.subn(r'<a\s+href=["\']404\.html["\']>\s*404\s*</a>', '', text, count=1, flags=re.I)
    write(path, new)
    return f"Removed 404 link from html-sitemap.html ({count} occurrence)"

def make_route_cards_static():
    path = ROOT / "routes.html"
    if not path.exists():
        return "routes.html missing"

    backup(path)
    text = read(path)

    pattern = r'<div\s+id=["\']routeResults["\']\s+class=["\']grid-2["\']\s*>\s*</div>'
    new, count = re.subn(pattern, ROUTE_CARDS, text, count=1, flags=re.I | re.S)

    if count == 0 and 'data-route-card' not in text:
        return "Could not find empty routeResults container"

    text = new if count else text
    write(path, text)
    return "Rendered 8 crawlable route cards directly in routes.html"

def mark_static_comparison_booking_links():
    path = ROOT / "routes.html"
    if not path.exists():
        return "routes.html missing"

    text = read(path)

    pattern = re.compile(
        r'<a\s+class="btn btn-primary"\s+href="booking\.html\?route=([^"]+)">Book Seat</a>'
    )

    def repl(match):
        slug = match.group(1)
        return f'<a class="btn btn-primary comparison-book-link" data-route="{slug}" href="booking.html?route={slug}">Book Seat</a>'

    text, count = pattern.subn(repl, text)
    write(path, text)
    return f"Updated {count} comparison-table booking button(s) to preserve date/passengers"

def replace_routes_js():
    path = ROOT / "js" / "routes.js"
    if not path.exists():
        return "js/routes.js missing"

    backup(path)
    write(path, ROUTES_JS)
    return "Reworked routes.js to filter static cards and keep homepage state separate"

def validate():
    problems = []

    sitemap = ROOT / "html-sitemap.html"
    if sitemap.exists() and re.search(r'href=["\']404\.html["\']', read(sitemap), flags=re.I):
        problems.append("html-sitemap.html still links to 404.html")

    routes_html = ROOT / "routes.html"
    if routes_html.exists():
        text = read(routes_html)
        if text.count("data-route-card") < 8:
            problems.append("routes.html does not contain 8 static route cards")
        if "comparison-book-link" not in text:
            problems.append("comparison-table booking links were not upgraded")

    routes_js = ROOT / "js" / "routes.js"
    if routes_js.exists():
        text = read(routes_js)
        if 'routeSearch.value = ""' not in text:
            problems.append("routeSearch is not being kept separate from origin/destination state")
        if "homepageState.origin" not in text or "homepageState.destination" not in text:
            problems.append("homepage origin/destination state missing")
        if "comparison-book-link" not in text:
            problems.append("comparison-table links are not updated from routes.js")

    if problems:
        print("\nVALIDATION FAILED")
        for problem in problems:
            print(" -", problem)
        return 1

    print("\nValidation passed.")
    return 0

def main():
    required = ["routes.html", "html-sitemap.html", "js/routes.js", "js/route-data.js"]
    missing = [name for name in required if not (ROOT / name).exists()]

    if missing:
        print("Run this file from the TRINITY-BUS2 project root.")
        print("Missing:", ", ".join(missing))
        return 2

    results = [
        remove_404_from_html_sitemap(),
        make_route_cards_static(),
        mark_static_comparison_booking_links(),
        replace_routes_js(),
    ]

    print("Trinity Bus Express route/SEO update:")
    for result in results:
        print(" -", result)

    return validate()

if __name__ == "__main__":
    sys.exit(main())
