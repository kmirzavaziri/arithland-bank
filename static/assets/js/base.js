const base = {
    initTimer: () => {
        const $navbarTime = $('#navbar-time');
        const updateTimer = function () {
            const currentTime = Math.abs($navbarTime.data("current-time"));
            const currentTimeSign = $navbarTime.data("current-time") < 0 ? -1 : 1;

            const newTime = currentTime + currentTimeSign;

            $navbarTime.data("current-time", currentTimeSign * newTime);

            const h = Math.floor((currentTime / 60) / 60);
            const m = Math.floor((currentTime / 60) % 60).toString().padStart(2, '0');
            const s = (currentTime % 60).toString().padStart(2, '0');

            $navbarTime.text(`${h}:${m}:${s}`);
        };

        setInterval(updateTimer, 1000);
    },
    initCompetitionSelection: () => {
        $(document).on('change', '.js-ab-submit', async function () {
            const form = $(this).closest('form')[0];
            const formData = new FormData(form);
            await fetch(form.action, {
                method: form.method || 'POST',
                body: formData
            });
            location.reload();
        });
    },
}

$(document).ready(function () {
    base.initTimer();
    base.initCompetitionSelection();

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
});
