document.addEventListener("DOMContentLoaded", () => {

    /* ========= SERVICES ========= */
    const serviceCards = document.querySelectorAll(".service-card");

    const serviceObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("animate");
                observer.unobserve(entry.target); // ✅ animate ONCE
            }
        });
    }, { threshold: 0.3 });

    serviceCards.forEach(card => serviceObserver.observe(card));


    /* ========= PRODUCTS ========= */
    const productCards = document.querySelectorAll(".product-card");

    const productObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show");
                observer.unobserve(entry.target); // ✅ animate ONCE
            }
        });
    }, { threshold: 0.25 });

    productCards.forEach(card => productObserver.observe(card));
});
