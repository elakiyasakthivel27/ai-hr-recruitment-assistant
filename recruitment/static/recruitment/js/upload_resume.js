
"use strict";

/* CURRENT DATE */

(function () {
    const dateElement = document.getElementById("currentDate");

    if (dateElement) {
        dateElement.textContent = new Intl.DateTimeFormat("en-IN", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }).format(new Date());
    }
})();


/* HR ACCOUNT DROPDOWN */

const accountToggle = document.getElementById("accountToggle");
const accountDropdown = document.getElementById("accountDropdown");

function closeAccountDropdown() {
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

        const opening = accountDropdown.hidden;

        accountDropdown.hidden = !opening;
        accountToggle.setAttribute("aria-expanded", String(opening));
    });

    document.addEventListener("click", function (event) {
        if (
            !accountDropdown.contains(event.target) &&
            !accountToggle.contains(event.target)
        ) {
            closeAccountDropdown();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeAccountDropdown();
        }
    });
}


/* RESUME FILE SELECTION */

const resumeInput = document.getElementById("resume");
const fileName = document.getElementById("fileName");
const dropArea = document.getElementById("dropArea");
const resumeForm = document.getElementById("resumeForm");

function updateFileName() {
    const file = resumeInput.files[0];

    fileName.textContent = file
        ? "Selected: " + file.name + " (" +
          (file.size / 1024 / 1024).toFixed(2) + " MB)"
        : "No file selected · Maximum 10 MB";
}

resumeInput.addEventListener("change", updateFileName);


/* DRAG AND DROP */

["dragenter", "dragover"].forEach(function (eventName) {
    dropArea.addEventListener(eventName, function (event) {
        event.preventDefault();
        dropArea.classList.add("dragover");
    });
});

["dragleave", "drop"].forEach(function (eventName) {
    dropArea.addEventListener(eventName, function (event) {
        event.preventDefault();
        dropArea.classList.remove("dragover");
    });
});

dropArea.addEventListener("drop", function (event) {
    if (event.dataTransfer.files.length) {
        resumeInput.files = event.dataTransfer.files;
        updateFileName();
    }
});


/* RESUME VALIDATION AND SUBMISSION */

resumeForm.addEventListener("submit", function (event) {
    const file = resumeInput.files[0];

    if (!file) {
        return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        event.preventDefault();
        alert("Please select a PDF resume.");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        event.preventDefault();
        alert("PDF must be 10 MB or smaller.");
        return;
    }

    const submitButton = resumeForm.querySelector(".submit-btn");

    submitButton.disabled = true;

    document.getElementById("submitLabel").textContent =
        "Uploading & evaluating resume…";
});
