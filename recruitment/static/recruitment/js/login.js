
"use strict";

// Vision Orbit - HR Login Password Visibility

const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

if (togglePassword && passwordInput) {
    togglePassword.addEventListener("click", function () {
        const showing = passwordInput.type === "text";

        passwordInput.type = showing ? "password" : "text";
        togglePassword.textContent = showing ? "Show" : "Hide";

        togglePassword.setAttribute(
            "aria-label",
            showing ? "Show password" : "Hide password"
        );

        togglePassword.setAttribute(
            "aria-pressed",
            String(!showing)
        );
    });
}
