$(document).on('submit', '#registerForm', function (event) {
    event.preventDefault();
    $("#registerFormBtn").attr('disabled', 'disabled')
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
            register_form.reset();
            $("#registerFormBtn").removeAttr('disabled')
            $('#signup-modal').modal('hide');
            $('#signin-modal').modal('show');
        },
        error: function (response) {
            if (response.status === 401) {
                $("#registerFormBtn").removeAttr('disabled')
                var errors = response["responseJSON"]["errors"]
                $('.invalid-feedback').css('display', 'none').text('');
                for (let i = 0; i < errors.length; i++) {
                    $("#err_" + errors[i]["field"]).text(errors[i]["error"]).css('display', 'block')
                }
            }

        }
    })
});


$(document).on('submit', '#LoginForm', function (event) {
    event.preventDefault();
    var register_form = $("#LoginForm")[0];
    var data = new FormData(register_form);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    var url = $("#LoginForm").attr('action');
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
            window.location.href = '/'
        },
        error: function (response) {
            if (response.status === 401) {
                var errors = response["responseJSON"]["errors"]
                $('.invalid-feedback').css('display', 'none').text('');
                for (let i = 0; i < errors.length; i++) {
                    $("#log_err_" + errors[i]["field"]).text(errors[i]["error"]).css('display', 'block')
                }
            }

        }
    })
});

$(document).on('submit', '#ForgotPasswordForm', function (event) {
    event.preventDefault();
    $("#ForgetPassBtn").attr('disabled', 'disabled')
    var form = $("#ForgotPasswordForm")[0];
    var data = new FormData(form);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    var url = $("#ForgotPasswordForm").attr('action');
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
            window.location.href = '/'
        },
        error: function (response) {
            if (response.status === 401) {
                $("#ForgetPassBtn").removeAttr('disabled')
                $('.invalid-feedback').css('display', 'none').text('');
                var errors = response["responseJSON"]["errors"]
                for (let i = 0; i < errors.length; i++) {
                    $("#fg_pass_err_" + errors[i]["field"]).text(errors[i]["error"]).css('display', 'block')
                }
            }

        }
    })
});

$(document).ready(function () {
    $("#forgotPassword").mouseup(function () {
        $('#signin-modal').modal('hide');
        $('#forgot-password-modal').modal('show');
    });
    $("#pageMessages").delay(12000).fadeOut(function () {
            $(this).remove();})
});

$(document).on('submit', '#EditInfoForm', function (event) {
    event.preventDefault();
    $("#EditInfoBtn").attr('disabled', 'disabled')
    var form = $("#EditInfoForm")[0];
    var data = new FormData(form);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    var url = $("#EditInfoForm").attr('action');
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
            window.location.href = '/edit-info/'
        },
        error: function (response) {
            if (response.status === 401) {
                $("#EditInfoBtn").removeAttr('disabled')
                var errors = response["responseJSON"]["errors"]
                $('.invalid-feedback').css('display', 'none').text('');
                for (let i = 0; i < errors.length; i++) {
                    $("#edit_info_err_" + errors[i]["field"]).text(errors[i]["error"]).css('display', 'block')
                }
            }

        }
    })
});

$(document).on('submit', '#emailAddressForm', function (event) {
    event.preventDefault();
    var email_address_form = $(this)[0];
    var data = new FormData(email_address_form);
    var token = $('input[name="csrfmiddlewaretoken"]').attr('value');
    var url = $(this).attr('action');
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
            email_address_form.reset();
            location.reload();
        },
        error: function (response) {
            alert('خطایی پیش آمده است')
        }
    })
});