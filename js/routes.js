const ROUTES = window.TBE_ROUTES || [];

function bookingUrl(route) {
  const current = new URLSearchParams(window.location.search);
  const next = new URLSearchParams({ route: route.slug });
  const date = current.get("date");
  const passengers = current.get("passengers");
  if (date) next.set("date", date);
  if (passengers) next.set("passengers", passengers);
  return `booking.html?${next.toString()}`;
}

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
          <a class="btn btn-primary" href="${bookingUrl(r)}">Request Seat</a>
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
});
