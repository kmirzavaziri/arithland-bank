const cw_request_widget = {
    requests: {},
    init: function () {
        $('.cw-request-widget').each(function () {
            const $widget = $(this);

            const target_input = $widget.data("target-input");
            const endpoint = $widget.data("endpoint");

            let request, timer;

            const rerender = function () {
                // todo send req if v changed
                if (timer) {
                    clearTimeout(timer);
                }
                if (request) {
                    request.abort();
                }

                timer = setTimeout(async function () {
                    request = $.ajax({
                        url: endpoint,
                        method: "POST",
                        contentType: "application/json",
                        headers: {
                            'X-CSRFToken':arithlandBank.csrfToken,
                        },
                        data: JSON.stringify({
                            [target_input]: $(`[name="${target_input}"]`).val(),
                        }),
                        success: function (response) {
                            let value = "cannot get balance";
                            console.log(response);
                            if ("value" in response) {
                                value = response.value;
                            }
                            $widget.html(value);
                        },
                        error: function (error) {
                            $widget.html("cannot get balance");
                        }
                    });
                }, 0);
            }

            $(`[name="${target_input}"]`).on("input change", rerender);
        });
    },
}

$(document).ready(function () {
    cw_request_widget.init();
});
