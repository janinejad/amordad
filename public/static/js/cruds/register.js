$(document).on('submit', '#registerForm', function (event) {
    event.preventDefault();
    var register_form = $("#registerForm")[0];
    var data = new FormData(register_form);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    var url = $("#registerForm").attr('action');
    $.ajaxSetup({
        beforeSend: function (xhr) {
            xhr.setRequestHeader('X-CSRFToken', token);
        }
    });
    $.ajax({
        url: url,
        type: 'post',
        dataType: 'json',
        cache: false,
        processData: false,
        contentType: false,
        data: data,
        success: function (data) {
            $("#successRegister").removeClass('d-none').addClass('show')
            register_form.reset();
            $('#signup-modal').modal('hide');
            $('#signin-modal').modal('show');
        },
        error: function (response) {
            if (response.status === 401) {
                var errors = response["responseJSON"]["errors"]
                for (let i = 0; i < errors.length; i++) {
                    $("#err_" + errors[i]["field"]).text(errors[i]["error"]).css('display', 'block')
                }
            }

        }
    })
});
