const ROUTES = [
  { slug: "nairobi-to-kampala", origin: "Nairobi", destination: "Kampala", country: "Uganda", flag: "🇺🇬", fare: 3500, duration: "12–14 hours", departure: "6:00 PM (Daily)", arrival: "7:00 AM next day", border: "Busia / Malaba OSBP", terminal: "River Road Terminal, Nairobi", stopovers: "Nakuru, Eldoret, Malaba, Jinja", bus: "Executive Luxury Coach" },
  { slug: "nairobi-to-kigali", origin: "Nairobi", destination: "Kigali", country: "Rwanda", flag: "🇷🇼", fare: 5500, duration: "18–20 hours", departure: "4:00 PM (Daily)", arrival: "11:00 AM next day", border: "Gatuna / Katuna OSBP", terminal: "River Road Terminal, Nairobi", stopovers: "Nakuru, Eldoret, Kampala, Gatuna", bus: "Executive Luxury Coach" },
  { slug: "nairobi-to-juba", origin: "Nairobi", destination: "Juba", country: "South Sudan", flag: "🇸🇸", fare: 7000, duration: "22–26 hours", departure: "2:00 PM (Mon, Wed, Sat)", arrival: "3:00 PM next day", border: "Nimule / Elegu Border", terminal: "Accra Road Terminal, Nairobi", stopovers: "Eldoret, Kampala, Gulu, Nimule", bus: "Cross-Border Express Coach" },
  { slug: "nairobi-to-goma", origin: "Nairobi", destination: "Goma", country: "DRC", flag: "🇨🇩", fare: 7500, duration: "24–28 hours", departure: "1:00 PM (Tue, Fri)", arrival: "5:00 PM next day", border: "Grande Barrière / Gisenyi", terminal: "Accra Road Terminal, Nairobi", stopovers: "Eldoret, Kampala, Kabale, Gisenyi", bus: "Cross-Border Express Coach" },
  { slug: "nairobi-to-bujumbura", origin: "Nairobi", destination: "Bujumbura", country: "Burundi", flag: "🇧🇮", fare: 7000, duration: "22–25 hours", departure: "3:00 PM (Wed, Sun)", arrival: "3:00 PM next day", border: "Akanyaru / Kanyaru Border", terminal: "River Road Terminal, Nairobi", stopovers: "Eldoret, Kampala, Kigali", bus: "Executive Luxury Coach" },
  { slug: "kampala-to-nairobi", origin: "Kampala", destination: "Nairobi", country: "Kenya", flag: "🇰🇪", fare: 3500, duration: "12–14 hours", departure: "6:00 PM (Daily)", arrival: "7:00 AM next day", border: "Malaba / Busia OSBP", terminal: "Bakuli Terminal, Sir Apollo Kaggwa Rd, Kampala", stopovers: "Jinja, Malaba, Eldoret, Nakuru", bus: "Executive Luxury Coach" },
  { slug: "kampala-to-kigali", origin: "Kampala", destination: "Kigali", country: "Rwanda", flag: "🇷🇼", fare: 2500, duration: "8–10 hours", departure: "8:00 PM (Daily)", arrival: "6:00 AM next day", border: "Gatuna OSBP", terminal: "Bakuli Terminal, Kampala", stopovers: "Masaka, Mbarara, Gatuna", bus: "Comfort Express Coach" },
  { slug: "kigali-to-nairobi", origin: "Kigali", destination: "Nairobi", country: "Kenya", flag: "🇰🇪", fare: 5500, duration: "18–20 hours", departure: "3:00 PM (Daily)", arrival: "10:00 AM next day", border: "Gatuna OSBP", terminal: "Nyabugogo Bus Park, Kigali", stopovers: "Gatuna, Kampala, Eldoret, Nakuru", bus: "Executive Luxury Coach" }
];

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("bookingForm");
  if (!form) return;

  const panels = [...document.querySelectorAll(".wizard-panel")];
  const navButtons = [...document.querySelectorAll(".wizard-nav button")];
  let currentStep = 0;
  let selectedSeats = [];

  // Populate Route Dropdown
  const routeSel = document.getElementById("route");
  routeSel.innerHTML = "";
  ROUTES.forEach(r => {
    const opt = document.createElement("option");
    opt.value = r.slug;
    opt.textContent = `${r.flag} ${r.origin} → ${r.destination} (${r.bus})`;
    routeSel.appendChild(opt);
  });

  // Check URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const routeParam = urlParams.get("route");
  if (routeParam && ROUTES.some(r => r.slug === routeParam)) {
    routeSel.value = routeParam;
  }

  // Pre-fill Date if not set
  const dateInput = document.getElementById("date");
  if (dateInput && !dateInput.value) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.value = tomorrow.toISOString().split("T")[0];
    dateInput.min = new Date().toISOString().split("T")[0];
  }

  function goToStep(i) {
    currentStep = Math.max(0, Math.min(i, panels.length - 1));
    panels.forEach((p, idx) => p.classList.toggle("active", idx === currentStep));
    navButtons.forEach((b, idx) => {
      b.classList.toggle("active", idx === currentStep);
      b.classList.toggle("completed", idx < currentStep);
    });
    updateSummary();
    window.scrollTo({ top: form.offsetTop - 90, behavior: "smooth" });
  }

  // Navigation handlers
  document.querySelectorAll("[data-next]").forEach(btn => {
    btn.onclick = () => {
      const activePanel = panels[currentStep];
      const inputs = [...activePanel.querySelectorAll("input, select")];
      let valid = true;
      inputs.forEach(inp => {
        if (!inp.checkValidity()) {
          valid = false;
          inp.reportValidity();
        }
      });
      if (!valid) return;

      if (currentStep === 2) {
        // Seat selection validation
        const passCount = parseInt(document.getElementById("passengers").value) || 1;
        if (selectedSeats.length !== passCount) {
          TBE.toast(`Please select exactly ${passCount} preferred seat(s)`);
          return;
        }
      }

      goToStep(currentStep + 1);
    };
  });

  document.querySelectorAll("[data-prev]").forEach(btn => {
    btn.onclick = () => goToStep(currentStep - 1);
  });

  navButtons.forEach((btn, idx) => {
    btn.onclick = () => {
      if (idx < currentStep) goToStep(idx);
    };
  });

  // Render Coach Seat Grid Layout
  function renderSeatMap() {
    const mapContainer = document.getElementById("seatMap");
    if (!mapContainer) return;

    mapContainer.innerHTML = "";

    // Seat Map Header / Driver Area
    const driverBar = document.createElement("div");
    driverBar.className = "coach-driver-row";
    driverBar.innerHTML = `
      <div class="driver-badge">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="9"/>
          <path d="M12 3v18M3 12h18"/>
        </svg>
        <span>Driver / Control Deck</span>
      </div>
      <div class="door-badge">Front Boarding Door 🚪</div>
    `;
    mapContainer.appendChild(driverBar);

    // Seat Layout Container: 2 + Walkway + 2
    const grid = document.createElement("div");
    grid.className = "coach-seat-grid";

    // 10 Rows of Seats (4 seats per row: A, B [aisle] C, D = 40 seats)
    const rows = 10;
    const cols = ["A", "B", "C", "D"];
    const reservedSeatNumbers = [3, 7, 12, 18, 25, 33]; // Sample realistic occupied seats

    for (let r = 1; r <= rows; r++) {
      const rowDiv = document.createElement("div");
      rowDiv.className = "coach-row";

      // Left Pair (A & B)
      ["A", "B"].forEach(col => {
        const seatNum = `${r}${col}`;
        const seatIndex = (r - 1) * 4 + (col === "A" ? 1 : 2);
        const isReserved = reservedSeatNumbers.includes(seatIndex);

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `seat-btn ${isReserved ? "reserved" : "available"} ${selectedSeats.includes(seatNum) ? "selected" : ""}`;
        btn.dataset.seat = seatNum;
        btn.disabled = isReserved;
        btn.setAttribute("aria-label", `Seat ${seatNum} ${isReserved ? "Occupied" : "Preferred"}`);
        btn.innerHTML = `<span class="seat-num">${seatNum}</span><span class="seat-type">${col === "A" ? "Win" : "Aisle"}</span>`;

        btn.onclick = () => handleSeatSelect(seatNum);
        rowDiv.appendChild(btn);
      });

      // Walkway Aisle Spacer
      const aisle = document.createElement("div");
      aisle.className = "coach-aisle";
      aisle.textContent = `${r}`;
      rowDiv.appendChild(aisle);

      // Right Pair (C & D)
      ["C", "D"].forEach(col => {
        const seatNum = `${r}${col}`;
        const seatIndex = (r - 1) * 4 + (col === "C" ? 3 : 4);
        const isReserved = reservedSeatNumbers.includes(seatIndex);

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = `seat-btn ${isReserved ? "reserved" : "available"} ${selectedSeats.includes(seatNum) ? "selected" : ""}`;
        btn.dataset.seat = seatNum;
        btn.disabled = isReserved;
        btn.setAttribute("aria-label", `Seat ${seatNum} ${isReserved ? "Occupied" : "Preferred"}`);
        btn.innerHTML = `<span class="seat-num">${seatNum}</span><span class="seat-type">${col === "D" ? "Win" : "Aisle"}</span>`;

        btn.onclick = () => handleSeatSelect(seatNum);
        rowDiv.appendChild(btn);
      });

      grid.appendChild(rowDiv);
    }

    mapContainer.appendChild(grid);
  }

  function handleSeatSelect(seatNum) {
    const maxPass = parseInt(document.getElementById("passengers").value) || 1;
    if (selectedSeats.includes(seatNum)) {
      selectedSeats = selectedSeats.filter(s => s !== seatNum);
    } else {
      if (selectedSeats.length >= maxPass) {
        TBE.toast(`You have selected ${maxPass} passenger(s). Change passenger count to select more seats.`);
        return;
      }
      selectedSeats.push(seatNum);
    }

    // Re-render seat active classes
    document.querySelectorAll(".seat-btn").forEach(btn => {
      const num = btn.dataset.seat;
      btn.classList.toggle("selected", selectedSeats.includes(num));
    });

    updateSummary();
  }

  function updateSummary() {
    const selectedSlug = routeSel.value;
    const route = ROUTES.find(r => r.slug === selectedSlug) || ROUTES[0];
    const passCount = parseInt(document.getElementById("passengers").value) || 1;
    const travelDate = document.getElementById("date").value || "Not set";
    const totalFare = route.fare * passCount;

    // Update Summary Sidebar / Card
    const elRoute = document.getElementById("summaryRoute");
    const elFare = document.getElementById("summaryFare");
    const elSeats = document.getElementById("summarySeats");
    const elTotal = document.getElementById("summaryTotal");
    const elTerminal = document.getElementById("summaryTerminal");
    const elDeparture = document.getElementById("summaryDeparture");

    if (elRoute) elRoute.textContent = `${route.flag} ${route.origin} → ${route.destination}`;
    if (elFare) elFare.textContent = TBE.money(route.fare) + " / seat";
    if (elSeats) elSeats.textContent = selectedSeats.length ? selectedSeats.join(", ") : `Selecting ${passCount} seat(s)...`;
    if (elTotal) elTotal.textContent = TBE.money(totalFare);
    if (elTerminal) elTerminal.textContent = route.terminal;
    if (elDeparture) elDeparture.textContent = `${route.departure} (Duration: ${route.duration})`;

    // Confirmation Review panel details
    const refEl = document.getElementById("bookingReference");
    if (refEl && (!refEl.textContent || refEl.textContent === "Generated after submission")) {
      refEl.textContent = TBE.ref();
    }
  }

  // Handle Form Submit (WhatsApp Request)
  form.addEventListener("submit", e => {
    e.preventDefault();
    const route = ROUTES.find(r => r.slug === routeSel.value) || ROUTES[0];
    const passCount = parseInt(document.getElementById("passengers").value) || 1;

    if (selectedSeats.length !== passCount) {
      TBE.toast(`Please select ${passCount} preferred seat(s) before continuing.`);
      goToStep(2);
      return;
    }

    const refCode = document.getElementById("bookingReference")?.textContent || TBE.ref();
    const name = form.name.value.trim();
    const phone = form.phone.value.trim();
    const email = form.email.value.trim() || "Not provided";
    const date = form.date.value;
    const specialRequest = form.request.value.trim() || "None";
    const totalFare = TBE.money(route.fare * passCount);

    const waMsg = `🚍 *TRINITY BUS EXPRESS - BOOKING REQUEST*
-----------------------------------------
🔖 *Booking Reference:* ${refCode}
👤 *Passenger Name:* ${name}
📞 *Phone Number:* ${phone}
✉️ *Email:* ${email}

📍 *Route:* ${route.origin} to ${route.destination} (${route.flag} ${route.country})
🚌 *Coach Type:* ${route.bus}
📅 *Travel Date:* ${date}
⏰ *Scheduled Departure:* ${route.departure}
🏢 *Departure Office:* ${route.terminal}
⏳ *Reporting Time:* 45 minutes prior to departure

💺 *Preferred Seat(s):* ${selectedSeats.join(", ")}
👥 *Passengers:* ${passCount}
💰 *Estimated Fare:* ${TBE.money(route.fare)} per seat
💵 *Estimated Total:* ${totalFare}

📝 *Special Request:* ${specialRequest}
-----------------------------------------
📌 *Note:* Seat choices & fares are subject to final confirmation by Trinity Bus Express office verification.`;

    const whatsappUrl = `${TBE.whatsapp}?text=${encodeURIComponent(waMsg)}`;
    window.open(whatsappUrl, "_blank");

    TBE.toast("Opening WhatsApp to send your booking request...");
  });

  // Event Listeners for inputs
  routeSel.addEventListener("change", () => {
    selectedSeats = [];
    renderSeatMap();
    updateSummary();
  });

  document.getElementById("passengers").addEventListener("change", () => {
    selectedSeats = [];
    renderSeatMap();
    updateSummary();
  });

  document.getElementById("date").addEventListener("change", updateSummary);

  // Initialize
  renderSeatMap();
  goToStep(0);
});
