$(document).on('keyup', '.filter-cats', function (event) {
    var input = $(this);
    var divs = input.parent().siblings()
    filter_items(input, divs)
});
$(document).on('change', '.selected-brand', function (event) {
    create_remove_label($(this).attr("data-lable"), $(this).val(), this.checked, 'brand')
});
$(document).on('change', '.selected-attribute', function (event) {
    create_remove_label($(this).attr("data-lable"), $(this).val(), this.checked, 'attr')
});

$(document).on('click', '.remove-filter', function (event) {
    var dataValue = $(this).attr('data-value');
    var dataType = $(this).attr('data-type');
    if (dataType == 'brand') {
        $("#brandCheckBox" + dataValue).prop('checked', false)
        $("#" + dataType + dataValue).remove();
    } else if (dataType == 'attr') {
        $("#attrCheckBox" + dataValue).prop('checked', false);
        $("#" + dataType + dataValue).remove();
    } else if (dataType == 'q') {
        $("#searchBoxTxt").remove();
    }
    remove_filter_box();
    $('#filter-form').submit()
});

$(document).ready(function () {
    // Target each form individually
    $('.search-form').on('submit', function (e) {
        // Find the input within the form being submitted
        var inputValue = $(this).find('.search-input').val().trim();

        // Check if the input is empty
        if (inputValue === "") {
            // Prevent form submission if input is empty
            e.preventDefault();
        }
    });
});
$(document).on('click', '#btnSearch', function (d) {
    var inputValue = $('#text-input-light').val().trim();
    if (inputValue.length > 0 ) {
        $('#filter-form').submit();
    }else {
        e.preventDefault();
    }
});
function remove_filter_box() {
    if ($("#applied-filters").children().length == 0) {
        $("#filter-box").hide();
    } else {
        $("#filter-box").show();
    }

}

$(document).ready(function () {
    remove_filter_box();
})

function create_remove_label(text, value, status, type) {
    var lblId = type + value
    if (status == true) {
        if ($("#" + lblId).length == 0) {
            var newlable = "<li id='" + lblId + "' class='nav-item mb-2 me-2'><button type='button' class='nav-link px-3 remove-filter' data-value='" + value + "' data-type='" + type + "'><i class=\"fi-x fs-xxs me-2\"></i>" + text + "</button></li>"
            $("#applied-filters").append(newlable);
        }
    } else {
        $("#" + lblId).remove()
    }
    remove_filter_box();
    $('#filter-form').submit()
}

function filter_items(input, divs) {
    var filter, lbl, i, txtValue;
    filter = input.val().toUpperCase();
    for (i = 0; i < divs.length; i++) {
        lbl = divs[i].getElementsByTagName("label")[0];
        txtValue = lbl.textContent || lbl.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            divs[i].style.display = "";
        } else {
            divs[i].style.display = "none";
        }
    }
}
