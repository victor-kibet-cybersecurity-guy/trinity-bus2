const ROUTES = window.TBE_ROUTES || [];

function localDateISO(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

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

  // Read route search values passed from the homepage/routes page.
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
    if (requestedDate && /^\d{4}-\d{2}-\d{2}$/.test(requestedDate) && requestedDate >= today) {
      dateInput.value = requestedDate;
    } else if (!dateInput.value) {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      dateInput.value = localDateISO(tomorrow);
    }
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
