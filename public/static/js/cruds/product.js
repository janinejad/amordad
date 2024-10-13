$(document).on('submit', '#add-favorite-form', function (event) {
    event.preventDefault();
    var add_favorite_form = $(this)[0];
    var data = new FormData(add_favorite_form);
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
            location.reload();
        },
        error: function (response) {
            if (response.status == 401) {
                var url = response["responseJSON"]["url"];
                window.location = url
            } else {
                alert('خطایی پیش آمده است')
            }
        }
    })
});

$(document).on('click', '.add-to-favorite', function (event) {
    $("#add-favorite-form").submit();
})

$(document).on('submit', '#add-to-cart-form', function (event) {
    event.preventDefault();
    $("#addToCartBtn").attr('disabled', 'disabled')
    var add_favorite_form = $(this)[0];
    var data = new FormData(add_favorite_form);
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
            window.location.href = '/cart/'
        },
        error: function (response) {
            if (response.status == 401) {
                $('#signin-modal').modal('show');
            }
            if (response.status === 400) {
                $("#addToCartBtn").removeAttr('disabled')
                var errors = response["responseJSON"]["errors"]
                $('.invalid-feedback').css('display', 'none').text('');
                for (let i = 0; i < errors.length; i++) {
                    $("#add_to_cart_err_" + errors[i]["field"]).text(errors[i]["error"]).css('display', 'block')
                }
            }
        }
    })
});

function calculate_price(id, qty) {
    $.ajax
    ({
        url: '/calculate-price/' + id + '/' + qty + '/',
        type: 'Get',
        datatype: 'JSON',
        success: function (data) {
            $('#perUnit').text(data["unit_d"] + ' ' + data["unit"]);
            $('#priceLbl').text(data["price"]);
            $('.regPrice').text(data["regular_price"]);
        },
        error: function (response) {
            alert('خطایی پیش امده است!')
        }
    });
}

$(document).on('change', '#number-input', function (event) {
    calculate_price($('#sc-condition').val(), $(this).val());
})

$(document).ready(function() {
    calculate_price($('#sc-condition').val(), 1);
});

$(document).on('change', '#sc-condition', function (event) {
    calculate_price($(this).val(), $(this).val());
})