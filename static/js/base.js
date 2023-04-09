const $buoop = {
    required: { e: -3, f: -3, o: -3, s: -1, c: -3 },
    insecure: true,
    unsupported: true,
    api: 2023.03,
};

function loadBrowserUpdateScript() {
    const browserUpdateScript = document.createElement("script");
    browserUpdateScript.src = "//browser-update.org/update.min.js";
    document.body.appendChild(browserUpdateScript);
}

document.addEventListener("DOMContentLoaded", loadBrowserUpdateScript, false);
window.addEventListener('load', loadBrowserUpdateScript);

const socket = io();
socket.on('connect', function () {
    console.log('Connected to server.');
    console.log(`Socket Id: ${socket.id}`);
    socket.emit('client-connect', {
        id: socket.id
    });
});

// Get the current year and update all elements with class "current-year"
$(document).ready(function () {
    const currentYear = new Date().getFullYear();
    $('.current-year').text(currentYear);
});

// Back to top button
const backToTopBtn = document.getElementById("backToTopBtn");

window.addEventListener("scroll", () => {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        backToTopBtn.style.display = "block";
    } else {
        backToTopBtn.style.display = "none";
    }
});

backToTopBtn.addEventListener("click", () => {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
});
