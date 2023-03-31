const $buoop = {
    required: { e: -3, f: -3, o: -3, s: -1, c: -3 },
    insecure: true,
    unsupported: true,
    api: 2023.03,
};

function $buo_f() {
    const e = document.createElement("script");
    e.src = "//browser-update.org/update.min.js";
    document.body.appendChild(e);
}

document.addEventListener("DOMContentLoaded", $buo_f, false);
window.addEventListener('load', $buo_f);

var socket = io();
socket.on('connect', function () {
    socket.emit('connect', { data: 'Successfully connected.' });
});