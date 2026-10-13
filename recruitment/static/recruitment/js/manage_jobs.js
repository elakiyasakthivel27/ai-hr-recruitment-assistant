
(function () {
    "use strict";

    // CURRENT DATE
    const dateElement = document.getElementById("currentDate");

    if (dateElement) {
        dateElement.textContent = new Intl.DateTimeFormat("en-IN", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }).format(new Date());
    }

    // SIDEBAR HR ACCOUNT DROPDOWN
    const accountToggle = document.getElementById("accountToggle");
    const accountDropdown = document.getElementById("accountDropdown");

    function closeSidebarAccount() {
        if (accountDropdown) {
            accountDropdown.hidden = true;
        }

        if (accountToggle) {
            accountToggle.setAttribute("aria-expanded", "false");
        }
    }

    if (accountToggle && accountDropdown) {
        accountToggle.addEventListener("click", function (event) {
            event.stopPropagation();

            const shouldOpen = accountDropdown.hidden;

            accountDropdown.hidden = !shouldOpen;

            accountToggle.setAttribute(
                "aria-expanded",
                String(shouldOpen)
            );
        });

        document.addEventListener("click", function (event) {
            if (
                !accountDropdown.contains(event.target) &&
                !accountToggle.contains(event.target)
            ) {
                closeSidebarAccount();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeSidebarAccount();
            }
        });
    }

    // TOP HR PROFILE DROPDOWN
    const topHrToggle = document.getElementById("topHrToggle");
    const topHrMenu = document.getElementById("topHrMenu");

    function closeTopHrMenu() {
        topHrMenu.hidden = true;
        topHrToggle.setAttribute("aria-expanded", "false");
    }

    if (topHrToggle && topHrMenu) {
        topHrToggle.addEventListener("click", function (event) {
            event.stopPropagation();

            const shouldOpen = topHrMenu.hidden;

            topHrMenu.hidden = !shouldOpen;

            topHrToggle.setAttribute(
                "aria-expanded",
                String(shouldOpen)
            );
        });

        document.addEventListener("click", function (event) {
            if (
                !topHrMenu.contains(event.target) &&
                !topHrToggle.contains(event.target)
            ) {
                closeTopHrMenu();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeTopHrMenu();
            }
        });
    }
})();
