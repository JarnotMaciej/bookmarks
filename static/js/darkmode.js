// darkmode.js

document.addEventListener("DOMContentLoaded", function () {
    const modeSwitch = document.getElementById("modeSwitch");
    const body = document.querySelector("body");

    modeSwitch.addEventListener("click", function () {
        if (body.dataset.bsTheme === "dark") {
            body.dataset.bsTheme = "light";
            modeSwitch.textContent = "Dark Mode";
        } else {
            body.dataset.bsTheme = "dark";
            modeSwitch.textContent = "Light Mode";
        }
    });

    // Check local storage for the last selected mode
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        body.dataset.bsTheme = savedTheme;
        if (savedTheme === "dark") {
            modeSwitch.textContent = "Light Mode";
        }
    }
});

// Save the selected mode to local storage
document.addEventListener("DOMContentLoaded", function () {
    const body = document.querySelector("body");
    body.addEventListener("themeChanged", function (event) {
        const newTheme = event.detail.theme;
        localStorage.setItem("theme", newTheme);
    });
});
