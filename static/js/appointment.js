document.addEventListener("DOMContentLoaded", function () {

  const slotButtons = document.querySelectorAll(".slot-btn");
  const selectedTimeInput = document.getElementById("selectedTime");
  const confirmBtn = document.getElementById("confirmBtn");
  const totalAmountSpan = document.getElementById("totalAmount");
  const selectedServicesContainer = document.getElementById("selectedServices");

  /* -----------------------------
     SLOT SELECTION
  ----------------------------- */
  slotButtons.forEach(btn => {
    btn.addEventListener("click", () => {

      slotButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      selectedTimeInput.value = btn.dataset.time;
      validateForm();
    });
  });

  /* -----------------------------
     REMOVE SERVICE
  ----------------------------- */
  selectedServicesContainer.addEventListener("click", function (e) {

    if (e.target.classList.contains("remove-service")) {

      const serviceItem = e.target.closest(".service-item");
      const serviceId = serviceItem.dataset.id;

      // remove UI
      serviceItem.remove();

      // remove hidden input
      const hidden = document.querySelector(
        `input.service-hidden[value="${serviceId}"]`
      );
      if (hidden) hidden.remove();

      updateTotal();
      validateForm();
    }
  });

  /* -----------------------------
     UPDATE TOTAL
  ----------------------------- */
  function updateTotal() {
    let total = 0;

    document.querySelectorAll(".service-item").forEach(item => {
      total += parseFloat(item.dataset.price);
    });

    totalAmountSpan.textContent = total.toFixed(2);
  }

  /* -----------------------------
     VALIDATION
  ----------------------------- */
  function validateForm() {
    const hasTime = selectedTimeInput.value !== "";
    const hasServices = document.querySelectorAll(".service-item").length > 0;

    confirmBtn.disabled = !(hasTime && hasServices);
  }

  updateTotal();
  validateForm();
});


document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.getElementById("booking_date");

    dateInput.addEventListener("click", function () {
        this.showPicker?.(); // Chrome / Edge
    });

    dateInput.addEventListener("focus", function () {
        this.showPicker?.();
    });
});
