document.addEventListener("DOMContentLoaded", function () {

  /* =========================
     ELEMENT REFERENCES
  ========================= */
  const monthLabel = document.getElementById("currentMonthLabel");
  const calendarGrid = document.getElementById("calendarGrid");
  const prevBtn = document.getElementById("prevMonth");
  const nextBtn = document.getElementById("nextMonth");
  const todayBtn = document.getElementById("goToday");

  const dayModal = document.getElementById("dayModal");
  const closeBtn = document.getElementById("closeDayModal");
  const modalDateTitle = document.getElementById("modalDateTitle");
  const modalAppointments = document.getElementById("modalAppointments");

  const searchInput = document.getElementById("modalSearch");
  const statusFilter = document.getElementById("modalStatus");

  let currentDate = new Date();

  /* =========================
     CALENDAR RENDER
  ========================= */
  function renderCalendar(date) {
    calendarGrid.innerHTML = "";

    const year = date.getFullYear();
    const month = date.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    monthLabel.textContent =
      date.toLocaleString("default", { month: "long" }) + " " + year;

    const startDayIndex = (firstDay.getDay() + 6) % 7;
    const totalDays = lastDay.getDate();

    for (let i = 0; i < startDayIndex; i++) {
      const empty = document.createElement("div");
      empty.className = "calendar-day muted";
      calendarGrid.appendChild(empty);
    }

    for (let day = 1; day <= totalDays; day++) {
      const dayCell = document.createElement("div");
      dayCell.className = "calendar-day empty-day";
      dayCell.dataset.statuses = "";

      const fullDate = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      dayCell.dataset.date = fullDate;

      const header = document.createElement("div");
      header.className = "day-header";

      const number = document.createElement("span");
      number.className = "day-number";
      number.textContent = day;

      header.appendChild(number);
      dayCell.appendChild(header);
      calendarGrid.appendChild(dayCell);
    }

    applyStatusIndicators(year, month);
  }

  /* =========================
     STATUS INDICATORS (DOTS)
  ========================= */
  function applyStatusIndicators(year, month) {
    const monthStr = `${year}-${String(month + 1).padStart(2, "0")}`;

    fetch(`/admin/api/appointment-status-summary?month=${monthStr}`)
      .then(res => res.json())
      .then(data => {
        Object.keys(data).forEach(date => {
          const dayCell = document.querySelector(
            `.calendar-day[data-date="${date}"]`
          );
          if (!dayCell) return;

          const status = data[date];
          const statuses = [];

          dayCell.classList.remove("empty-day");

          const old = dayCell.querySelector(".status-indicators");
          if (old) old.remove();

          const indicators = document.createElement("div");
          indicators.className = "status-indicators";

          if (status.pending > 0) {
            indicators.innerHTML += `<span class="status-dot pending"></span>`;
            statuses.push("PENDING");
          }
          if (status.confirmed > 0) {
            indicators.innerHTML += `<span class="status-dot confirmed"></span>`;
            statuses.push("CONFIRMED");
          }
          if (status.completed > 0) {
            indicators.innerHTML += `<span class="status-dot completed"></span>`;
            statuses.push("COMPLETED");
          }

          dayCell.dataset.statuses = statuses.join(",");
          dayCell.appendChild(indicators);
        });

        filterCalendarByStatus(statusFilter?.value || "");
      });
  }

  /* =========================
     FADE FILTER (STATUS)
  ========================= */
  function filterCalendarByStatus(selectedStatus) {
    const days = document.querySelectorAll(".calendar-day:not(.muted)");

    days.forEach(day => {
      const statuses = day.dataset.statuses;

      if (!selectedStatus) {
        day.style.opacity = "1";
        day.style.pointerEvents = "auto";
        return;
      }

      if (!statuses) {
        day.style.opacity = "0.3";
        day.style.pointerEvents = "none";
        return;
      }

      const match = statuses.split(",").includes(selectedStatus);
      day.style.opacity = match ? "1" : "0.3";
      day.style.pointerEvents = match ? "auto" : "none";
    });
  }

  if (statusFilter) {
    statusFilter.addEventListener("change", function () {
      filterCalendarByStatus(this.value);
    });
  }

  /* =========================
     SEARCH HIGHLIGHT (NEW)
  ========================= */
  function highlightDatesBySearch(query) {
    const days = document.querySelectorAll(".calendar-day[data-date]");

    // reset first
    days.forEach(day => {
      day.classList.remove("search-match");
      day.style.opacity = "1";
      day.style.pointerEvents = "auto";
    });

    if (!query) {
      filterCalendarByStatus(statusFilter?.value || "");
      return;
    }

    fetch(`/admin/api/appointment-search-dates?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(dates => {
        days.forEach(day => {
          if (dates.includes(day.dataset.date)) {
            day.classList.add("search-match");
          } else {
            day.style.opacity = "0.3";
            day.style.pointerEvents = "none";
          }
        });
      });
  }

  if (searchInput) {
    let searchTimer;

    searchInput.addEventListener("input", function () {
      console.log("Typed:", this.value);
      clearTimeout(searchTimer);
      const query = this.value.trim();

      searchTimer = setTimeout(() => {
        highlightDatesBySearch(query);
      }, 300);
    });
  }

  /* MONTH NAVIGATION */
  
  prevBtn.onclick = () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar(currentDate);
  };
  
  todayBtn.onclick = () => {

    currentDate = new Date();
   currentDate.setDate(1); 
   renderCalendar(currentDate)
  };
  

  nextBtn.onclick = () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar(currentDate);
  };

  /* DAY CLICK → MODAL */
  calendarGrid.addEventListener("click", (e) => {
    const cell = e.target.closest(".calendar-day:not(.muted)");
    if (!cell || cell.style.pointerEvents === "none") return;

    const date = cell.dataset.date;
    modalDateTitle.textContent = date;
    modalAppointments.innerHTML = "<p>Loading appointments...</p>";

    fetch(`/admin/api/appointments-by-date?date=${date}`)
      .then(res => res.json())
      .then(data => {
        modalAppointments.innerHTML = data.length
          ? data.map(appt => `
              <div class="modal-appointment-item">
                <div>
                  <strong>${appt.client_name}</strong><br>
                  ${appt.service_name}
                </div>
                <div class="text-end">
                  ${appt.appointment_time}<br>
                  <span class="status-badge status-${appt.status.toLowerCase()}">
                    ${appt.status}
                  </span>
                </div>
              </div>
            `).join("")
          : "<p>No appointments found.</p>";
      });

    dayModal.classList.add("open");
  });

  closeBtn.onclick = () => dayModal.classList.remove("open");

  /* =========================
     SUMMARY COUNTS
  ========================= */
  function loadSummaryCounts() {
    fetch("/admin/api/appointment-summary-counts")
      .then(res => res.json())
      .then(data => {
        document.getElementById("todayCount").textContent = data.today;
        document.getElementById("weekCount").textContent = data.week;
        document.getElementById("monthCount").textContent = data.month;
      });
  }

  /* =========================
     INITIAL LOAD
  ========================= */
  renderCalendar(currentDate);
  loadSummaryCounts();

});
