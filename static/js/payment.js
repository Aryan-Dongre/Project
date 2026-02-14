function enableEmailEdit() {
    const input = document.getElementById("emailInput");
    input.removeAttribute("readonly");
    input.focus();

    input.addEventListener("blur", () => {
        input.setAttribute("readonly", true);
    });
}
