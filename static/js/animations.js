document.addEventListener("DOMContentLoaded", () => {
    // Fade in elements on load
    document.querySelectorAll(".persona-card, .debate-message").forEach(el => {
        el.style.opacity = 0;
        setTimeout(() => {
            el.style.transition = "opacity 0.5s";
            el.style.opacity = 1;
        }, 100);
    });
});
