
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

/* HR ACCOUNT - CLICK ANYWHERE */

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
}

/* READ INSIGHTS DATA */

let candidateInsights = {};

try {
    const jsonElement = document.getElementById(
        "candidate-insights-data"
    );

    if (jsonElement) {
        candidateInsights = JSON.parse(jsonElement.textContent);
    }
} catch (error) {
    console.error("Could not load candidate insights:", error);
}

/* HELPERS */

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? "";
    }
}

function normalizeSkills(skills) {
    if (Array.isArray(skills)) {
        return skills.filter(Boolean);
    }

    if (typeof skills === "string") {
        return skills
            .split(",")
            .map(skill => skill.trim())
            .filter(Boolean);
    }

    return [];
}

function renderSkills(id, skills, type) {
    const container = document.getElementById(id);

    if (!container) return;

    container.replaceChildren();

    const items = normalizeSkills(skills);

    if (!items.length) {
        const empty = document.createElement("span");
        empty.className = "candidate-email";
        empty.textContent = "None detected";
        container.appendChild(empty);
        return;
    }

    items.forEach(function (skill) {
        const chip = document.createElement("span");

        chip.className = "skill-chip " + type;
        chip.textContent = skill;

        container.appendChild(chip);
    });
}

function renderQuestions(questions) {
    const list = document.getElementById("modalQuestions");

    if (!list) return;

    list.replaceChildren();

    const items = Array.isArray(questions) ? questions : [];

    if (!items.length) {
        const item = document.createElement("li");
        item.textContent = "No interview questions available.";
        list.appendChild(item);
        return;
    }

    items.forEach(function (question) {
        const item = document.createElement("li");
        item.textContent = question;
        list.appendChild(item);
    });
}

/* OPEN INSIGHTS */

function openAiModal(button) {
    const candidateId = String(
        button.dataset.candidateId || ""
    );

    const data = candidateInsights[candidateId];

    if (!data) {
        alert(
            "Candidate insights unavailable. Please refresh the dashboard."
        );
        return;
    }

    setText(
        "modalCandidateName",
        button.dataset.name || "Candidate"
    );

    setText(
        "modalCandidateRole",
        button.dataset.role || "General Screening"
    );

    const score = Number(
        button.dataset.score ??
        data.score ??
        data.match_score ??
        0
    );

    const scoreElement = document.getElementById("modalMatchScore");

    if (scoreElement) {
        scoreElement.textContent = score.toFixed(0) + "%";

        scoreElement.style.color =
            score >= 70 ? "#60e5b7" :
            score >= 45 ? "#ffd076" :
            "#ff8ea6";
    }

    const matched = normalizeSkills(data.matched_skills);
    const missing = normalizeSkills(data.missing_skills);

    setText(
        "matchedCount",
        String(matched.length).padStart(2, "0")
    );

    setText(
        "missingCount",
        String(missing.length).padStart(2, "0")
    );

    renderSkills("modalMatched", matched, "matched");
    renderSkills("modalMissing", missing, "missing");

    setText(
        "modalSummary",
        data.summary || "No profile summary available."
    );

    renderQuestions(data.questions);

    const resumeLink = document.getElementById("modalResumeLink");
    const resumeUrl = button.dataset.resume;

    if (resumeLink) {
        if (resumeUrl) {
            resumeLink.href = resumeUrl;
            resumeLink.classList.remove("disabled");
            resumeLink.removeAttribute("aria-disabled");
            resumeLink.textContent = "▤ Open Candidate Resume ↗";
        } else {
            resumeLink.removeAttribute("href");
            resumeLink.classList.add("disabled");
            resumeLink.setAttribute("aria-disabled", "true");
            resumeLink.textContent = "Resume Not Available";
        }
    }

    const modal = document.getElementById("aiModal");

    if (modal) {
        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");

        document.getElementById("closeModalButton")?.focus();
    }
}

/* CLOSE INSIGHTS */

function closeAiModal() {
    const modal = document.getElementById("aiModal");

    if (modal) {
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-open");
    }
}

/* EVENT LISTENERS */

document.querySelectorAll(".insight-button").forEach(function (button) {
    button.addEventListener("click", function () {
        openAiModal(button);
    });
});

document.getElementById("closeModalButton")
    ?.addEventListener("click", closeAiModal);

document.getElementById("aiModal")
    ?.addEventListener("click", function (event) {
        if (event.target === this) {
            closeAiModal();
        }
    });

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeAiModal();
        closeAccountDropdown();
    }
});
