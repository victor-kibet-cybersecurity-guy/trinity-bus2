const ROUTES = window.TBE_ROUTES || [];

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
