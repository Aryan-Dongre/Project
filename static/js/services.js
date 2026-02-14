console.log("services.js loaded");

document.addEventListener("DOMContentLoaded", function () {

    // CARD SELECTION
    document.querySelectorAll(".service-card").forEach(card => {
        const checkbox = card.querySelector(".service-checkbox");

        card.addEventListener("click", function (e) {
            if (e.target.tagName === "INPUT") return;

            checkbox.checked = !checkbox.checked;
            card.classList.toggle("selected", checkbox.checked);
        });

        checkbox.addEventListener("change", function () {
            card.classList.toggle("selected", checkbox.checked);
        });
    });

    // BOOK APPOINTMENT
    const bookBtn = document.getElementById("bookAppointmentBtn");

    if (!bookBtn) {
        console.error("Book Appointment button not found");
        return;
    }

    bookBtn.addEventListener("click", function () {

        const selectedServices = [];

        document.querySelectorAll(".service-checkbox:checked").forEach(cb => {
            selectedServices.push(cb.value);
        });

        if (selectedServices.length === 0) {
            alert("Please select at least one service");
            return;
        }

        fetch("/set_selected_services", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ services: selectedServices })
        })
        .then(() => {
            window.location.href = "/appointment";
        });
    });

});

