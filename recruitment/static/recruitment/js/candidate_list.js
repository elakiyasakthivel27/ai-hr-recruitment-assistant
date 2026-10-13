
"use strict";

(function () {

    /* CURRENT DATE */

    const dateElement = document.getElementById("today-date");

    if (dateElement) {
        dateElement.textContent = new Intl.DateTimeFormat("en-GB", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }).format(new Date());
    }


    /* HR ACCOUNT DROPDOWNS */

    const toggles = [
        [
            document.getElementById("sidebar-account-toggle"),
            document.getElementById("sidebar-account-menu")
        ],
        [
            document.getElementById("top-account-toggle"),
            document.getElementById("top-account-menu")
        ]
    ].filter(([button, menu]) => button && menu);

    function closeAccountMenus() {
        toggles.forEach(([button, menu]) => {
            menu.hidden = true;
            button.setAttribute("aria-expanded", "false");
        });
    }

    toggles.forEach(([button, menu]) => {

        button.addEventListener("click", function (event) {
            event.stopPropagation();

            const shouldOpen = menu.hidden;

            closeAccountMenus();

            menu.hidden = !shouldOpen;

            button.setAttribute(
                "aria-expanded",
                String(shouldOpen)
            );
        });

        menu.addEventListener("click", function (event) {
            event.stopPropagation();
        });

    });

    document.addEventListener("click", closeAccountMenus);

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeAccountMenus();
        }
    });


    /* CANDIDATE ROW SELECTION */

    const candidateRows = document.querySelectorAll(
        ".table-wrap tbody tr"
    );

    candidateRows.forEach(function (row) {

        if (row.querySelector(".empty")) {
            return;
        }

        row.addEventListener("click", function (event) {

            if (event.target.closest("a, button, input, select")) {
                return;
            }

            candidateRows.forEach(function (other) {
                other.classList.remove("candidate-row-selected");
            });

            row.classList.add("candidate-row-selected");

        });

    });


    /* MATCHED AND MISSING SKILLS */

    document.querySelectorAll(".skill-cell").forEach(function (cell) {

        const original = cell.textContent.trim();

        if (
            !original ||
            /^(not available|none|n\/a|null|\[\])$/i.test(original)
        ) {
            cell.textContent = "";

            const empty = document.createElement("span");
            empty.className = "skill-empty";
            empty.textContent = "Not available";

            cell.appendChild(empty);
            return;
        }

        const values = original
            .split(",")
            .map(skill => skill.trim())
            .filter(Boolean);

        if (!values.length) {
            return;
        }

        cell.textContent = "";

        const wrapper = document.createElement("div");
        wrapper.className = "skill-tags";

        values.forEach(function (value) {

            const tag = document.createElement("span");

            tag.className =
                "skill-tag" +
                (cell.dataset.skillType === "missing" ? " missing" : "");

            tag.textContent = value;

            wrapper.appendChild(tag);

        });

        cell.appendChild(wrapper);

    });

})();
