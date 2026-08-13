const ROUTES = [
  { slug: "nairobi-to-kampala", origin: "Nairobi", destination: "Kampala", country: "Uganda", flag: "🇺🇬", fare: 3500, duration: "12–14 hours", departure: "6:00 PM (Daily)", arrival: "7:00 AM next day", border: "Busia / Malaba OSBP", stopovers: "Nakuru, Eldoret, Malaba, Jinja", bus: "Executive Luxury Coach" },
  { slug: "nairobi-to-kigali", origin: "Nairobi", destination: "Kigali", country: "Rwanda", flag: "🇷🇼", fare: 5500, duration: "18–20 hours", departure: "4:00 PM (Daily)", arrival: "11:00 AM next day", border: "Gatuna / Katuna OSBP", stopovers: "Nakuru, Eldoret, Kampala, Gatuna", bus: "Executive Luxury Coach" },
  { slug: "nairobi-to-juba", origin: "Nairobi", destination: "Juba", country: "South Sudan", flag: "🇸SS", fare: 7000, duration: "22–26 hours", departure: "2:00 PM (Mon, Wed, Sat)", arrival: "3:00 PM next day", border: "Nimule / Elegu Checkpoint", stopovers: "Eldoret, Kampala, Gulu, Nimule", bus: "Cross-Border Express Coach" },
  { slug: "nairobi-to-goma", origin: "Nairobi", destination: "Goma", country: "DRC", flag: "🇨🇩", fare: 7500, duration: "24–28 hours", departure: "1:00 PM (Tue, Fri)", arrival: "5:00 PM next day", border: "Grande Barrière / Gisenyi", stopovers: "Eldoret, Kampala, Kabale, Gisenyi", bus: "Cross-Border Express Coach" },
  { slug: "nairobi-to-bujumbura", origin: "Nairobi", destination: "Bujumbura", country: "Burundi", flag: "🇧🇮", fare: 7000, duration: "22–25 hours", departure: "3:00 PM (Wed, Sun)", arrival: "3:00 PM next day", border: "Kanyaru / Akanyaru Border", stopovers: "Eldoret, Kampala, Kigali", bus: "Executive Luxury Coach" },
  { slug: "kampala-to-nairobi", origin: "Kampala", destination: "Nairobi", country: "Kenya", flag: "🇰🇪", fare: 3500, duration: "12–14 hours", departure: "6:00 PM (Daily)", arrival: "7:00 AM next day", border: "Malaba / Busia OSBP", stopovers: "Jinja, Malaba, Eldoret, Nakuru", bus: "Executive Luxury Coach" },
  { slug: "kampala-to-kigali", origin: "Kampala", destination: "Kigali", country: "Rwanda", flag: "🇷🇼", fare: 2500, duration: "8–10 hours", departure: "8:00 PM (Daily)", arrival: "6:00 AM next day", border: "Gatuna OSBP", stopovers: "Masaka, Mbarara, Gatuna", bus: "Comfort Express Coach" },
  { slug: "kigali-to-nairobi", origin: "Kigali", destination: "Nairobi", country: "Kenya", flag: "🇰🇪", fare: 5500, duration: "18–20 hours", departure: "3:00 PM (Daily)", arrival: "10:00 AM next day", border: "Gatuna OSBP", stopovers: "Gatuna, Kampala, Eldoret, Nakuru", bus: "Executive Luxury Coach" }
];

function renderRoutes(data = ROUTES) {
  const out = document.getElementById("routeResults");
  if (!out) return;

  if (data.length === 0) {
    out.innerHTML = `<div class="card" style="grid-column: 1/-1; text-align: center; padding: 40px;">
      <h3>No routes matched your search.</h3>
      <p class="muted">Try adjusting your origin or destination filter.</p>
    </div>`;
    return;
  }

  out.innerHTML = data.map(r => `
    <article class="card route-card">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
        <span class="pill">${r.flag} ${r.country}</span>
        <button class="favorite" data-slug="${r.slug}" aria-label="Favorite route">♡</button>
      </div>

      <h3 style="font-size: 1.35rem; margin-bottom: 8px;">${r.origin} → ${r.destination}</h3>
      
      <div style="font-size: 0.92rem; color: var(--muted); margin-bottom: 14px; line-height: 1.6;">
        <p style="margin: 3px 0;">⏰ <strong>Departure:</strong> ${r.departure}</p>
        <p style="margin: 3px 0;">⏳ <strong>Est. Duration:</strong> ${r.duration}</p>
        <p style="margin: 3px 0;">🛂 <strong>Border Post:</strong> ${r.border}</p>
        <p style="margin: 3px 0;">📍 <strong>Key Stops:</strong> ${r.stopovers}</p>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: baseline; border-top: 1px solid var(--border); padding-top: 12px; margin-top: 12px;">
        <div>
          <small class="muted" style="display: block;">Est. Starting Fare</small>
          <strong class="price" style="font-size: 1.4rem;">${TBE.money(r.fare)}</strong>
        </div>
        <div class="actions" style="margin: 0;">
          <a class="btn btn-primary" href="booking.html?route=${r.slug}">Request Seat</a>
          <a class="btn btn-outline" href="routes/${r.slug}.html">Guide</a>
        </div>
      </div>
    </article>
  `).join("");

  bindFavs();
}

function bindFavs() {
  const saved = JSON.parse(localStorage.getItem("tbe-favorites") || "[]");
  document.querySelectorAll(".favorite").forEach(b => {
    const slug = b.dataset.slug;
    const isFav = saved.includes(slug);
    b.classList.toggle("active", isFav);
    b.textContent = isFav ? "♥" : "♡";
    b.onclick = () => {
      let favs = JSON.parse(localStorage.getItem("tbe-favorites") || "[]");
      favs = favs.includes(slug) ? favs.filter(x => x !== slug) : [...favs, slug];
      localStorage.setItem("tbe-favorites", JSON.stringify(favs));
      renderRoutes(filter());
    };
  });
}

function filter() {
  const q = (document.getElementById("routeSearch")?.value || "").toLowerCase();
  const country = document.getElementById("countryFilter")?.value || "";
  const sort = document.getElementById("routeSort")?.value || "";

  let d = ROUTES.filter(r => {
    const textMatch = (r.origin + " " + r.destination + " " + r.country + " " + r.stopovers + " " + r.border).toLowerCase().includes(q);
    const countryMatch = !country || r.country === country;
    return textMatch && countryMatch;
  });

  if (sort === "fare") d.sort((a, b) => a.fare - b.fare);
  if (sort === "duration") d.sort((a, b) => parseInt(a.duration) - parseInt(b.duration));

  return d;
}

document.addEventListener("DOMContentLoaded", () => {
  renderRoutes();
  ["routeSearch", "countryFilter", "routeSort"].forEach(id => {
    document.getElementById(id)?.addEventListener("input", () => renderRoutes(filter()));
  });
});
