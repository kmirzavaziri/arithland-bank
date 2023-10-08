const base = {
    initTimer: function () {
        const $navbarTime = $('#navbar-time');
        const updateTimer = function () {
            const currentTime = $navbarTime.data("current-time") + 1;
            $navbarTime.data("current-time", currentTime);

            const h = Math.floor((currentTime / 60) / 60);
            const m = Math.floor((currentTime / 60) % 60).toString().padStart(2, '0');
            const s = (currentTime % 60).toString().padStart(2, '0');

            $navbarTime.text(`${h}:${m}:${s}`);
        };

        setInterval(updateTimer, 1000);
    },
}

$(document).ready(function () {
    base.initTimer();
});
