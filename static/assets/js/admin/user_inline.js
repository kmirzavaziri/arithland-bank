const user_inline = {
    init: () => {
        $(document).on('change', '[id^=id_user_set-][id$=-existing_user]', function () {
            const userId = $(this).val();
            const rowPrefix = $(this).attr('id').match(/id_user_set-(\d+)-existing_user/)[1];

            if (userId) {
                $.ajax({
                    url: `/api/admin/get-user-details/${userId}`,
                    success: function (data) {
                        $('#id_user_set-' + rowPrefix + '-username').val(data.username);
                    }
                });
            } else {
                $('#id_user_set-' + rowPrefix + '-username').val('');
            }
        });
    },
};
window.addEventListener('load', function () {
    $(document).ready(function () {
        user_inline.init();
    });
});
