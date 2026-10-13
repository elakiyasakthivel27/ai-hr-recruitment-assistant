
(function () {
    "use strict";

    // Current date
    const dateElement = document.getElementById("currentDate");

    if (dateElement) {
        dateElement.textContent = new Intl.DateTimeFormat("en-IN", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }).format(new Date());
    }

    // Sidebar HR account dropdown
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

    // Top HR profile dropdown
    const topHrToggle = document.getElementById("topHrToggle");
    const topHrMenu = document.getElementById("topHrMenu");

    function closeTopHrMenu() {
        if (topHrMenu) {
            topHrMenu.hidden = true;
        }

        if (topHrToggle) {
            topHrToggle.setAttribute("aria-expanded", "false");
        }
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

    // Candidate comparison validation
    const compareForm = document.getElementById("compareForm");
    const candidate1 = document.getElementById("candidate1");
    const candidate2 = document.getElementById("candidate2");
    const compareError = document.getElementById("compareError");

    if (compareForm && candidate1 && candidate2) {
        compareForm.addEventListener("submit", function (event) {
            if (
                candidate1.value &&
                candidate1.value === candidate2.value
            ) {
                event.preventDefault();

                if (compareError) {
                    compareError.style.display = "block";
                }

                candidate2.focus();
            } else if (compareError) {
                compareError.style.display = "none";
            }
        });

        [candidate1, candidate2].forEach(function (select) {
            select.addEventListener("change", function () {
                if (compareError) {
                    compareError.style.display = "none";
                }
            });
        });
    }
})();
