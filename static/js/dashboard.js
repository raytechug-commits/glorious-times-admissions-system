
document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const menuButton = document.getElementById("menuButton");
    const searchInput = document.getElementById("applicationSearch");
    const applicationRows = document.querySelectorAll("#applicationRows tr");

    // Mobile sidebar
    if (sidebar && menuButton) {
        menuButton.addEventListener("click", function () {
            const isOpen = sidebar.classList.toggle("is-open");
            menuButton.setAttribute("aria-expanded", String(isOpen));
        });

        document.addEventListener("click", function (event) {
            if (
                window.innerWidth <= 760 &&
                sidebar.classList.contains("is-open") &&
                !sidebar.contains(event.target) &&
                !menuButton.contains(event.target)
            ) {
                sidebar.classList.remove("is-open");
                menuButton.setAttribute("aria-expanded", "false");
            }
        });
    }

    // Search the applications currently displayed in the table
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const query = searchInput.value.trim().toLowerCase();

            applicationRows.forEach(function (row) {
                const matches = row.textContent.toLowerCase().includes(query);
                row.hidden = !matches;
            });
        });
    }
});
