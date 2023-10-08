const vw_sum_widget = {
    init: function () {
        $('.cw-sum-widget').each(function () {
            const $widget = $(this);
            const rerender = function () {
                let sum = 0;
                for (let i = 0; i < target_inputs.length; i++) {
                    sum += $(`[name="${target_inputs[i].name}"]`).val() * target_inputs[i].weight;
                }
                $widget.html(sum);
            }

            const target_inputs = $widget.data("target-inputs");
            for (let i = 0; i < target_inputs.length; i++) {
                $(`[name="${target_inputs[i].name}"]`).on("input change", rerender);
            }

            rerender();
        });
    },
}

$(document).ready(function () {
    vw_sum_widget.init();
});
