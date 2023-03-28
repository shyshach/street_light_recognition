$(function() {
  $('input[name="daterange"]').daterangepicker({
    opens: 'center'
  }, function(start, end, label) {
    console.log("A new date selection was made: " + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD'));
  });
});

function toTimestamp(strDate){
   var datum = Date.parse(strDate);
   return datum/1000;
}

function getHouse(street, result_tag, value_type){
   $.ajax({
        url: "/get_houses",
        type: "get",
        data: {
            "street_id": street
        },
        success: function(response) {
            res = '<option value="all" selected>Select house</option>'
            $.each(response, function(item, value ) {
                res = res + '<option value="' + value[value_type] + '">' + value['number'] + '</option>'
            });
            $(result_tag).html(res)
        },
        error: function(xhr) {
            alert('Request failed!')
        }
   });
}

function getStreet(city, result_tag, value_type){
   $.ajax({
        url: "/get_streets",
        type: "get",
        data: {
            "city": city
        },
        success: function(response) {
            res = '<option value="all" selected>Select street</option>'
            $.each(response, function(item, value ) {
                res = res + '<option value="' + value[value_type] + '">' + value['street_name'] + '</option>'
            });
            $(result_tag).html(res)
        },
        error: function(xhr) {
            alert('Request failed!')
        }
   });
}

$(document).ready(function(){
    $('#dates').val('Select dates');
    $('#apply_dates').click(function(){
        // filter by dates
        dates = $('#dates').val().split(' - ');
        start_date = toTimestamp(dates[0]);
        end_date = toTimestamp(dates[1]) + 24*60*60;
        $('#history_table tr').show();
        $('#history_table .timestamp').each(function(){
            current_stamp = toTimestamp($(this).text());
            if (current_stamp < start_date || current_stamp > end_date) {
                $(this).parent().hide();
            }
        });

        // filter by house
        filter_house = $('#filter_house').val();
        console.log(filter_house)
        $('#history_table .house_th').slice(1).each(function(){
            current_th = $(this).text();
            if (current_th != filter_house && filter_house!='all') {
                $(this).parent().hide();
            }
        });

        // filter by street
        filter_street = $('#filter_street option:selected').text();
        $('#history_table .street_th').slice(1).each(function(){
            current_th = $(this).text();
            if (current_th != filter_street && filter_street!='Select street') {

                $(this).parent().hide();
            }
        });

        // filter by city
        filter_city = $('#filter_city option:selected').text();
        $('#history_table .city_th').slice(1).each(function(){
            current_th = $(this).text();
            if (current_th != filter_city && filter_street!='all') {
                $(this).parent().hide();
            }
        });

    });

    $('#refresh_dates').click(function(){
        $('#history_table tr').show();
        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var yyyy = today.getFullYear();
        today = mm + '/' + dd + '/' + yyyy;
        $('#dates').data('daterangepicker').setStartDate(today);
        $('#dates').data('daterangepicker').setEndDate(today);
        $('#dates').val('Select dates');
        $('#filter_house').val('all')
    });

    $('#retrieve').click(function(){
       $.ajax({
       url: "/get_prediction",
       type: "get",
       success: function(response) {
            $("#wordResult").html(response.luminosity)
            $("#image_update").attr('src', response.img);
            new_house_id = $("#house_id").val();
            if (new_house_id == '') {
                new_house_id = $("#add_house").val()
            }

            $.ajax({
                url: "/add_record",
                type: "post",
                data: {
                    "house_id": new_house_id,
                    "original_photo": response.original_img,
                    "processed_photo": response.img,
                    "quantity": response.luminosity
                },
                success: function(raw) {
                    if (raw.error){
                        alert(raw.error)
                    } else {
                        if ($('#add_city').val()) {
                            new_row = `<tr data-index="0"><td>${raw.city}</td>`
                        }
                        else {
                            new_row = `<tr data-index="0">`
                        }
                        new_row = new_row + `<td>${raw.house_number}</td><td>${raw.street}</td>
                        <td><a href="${response.original_img}">link</a></td>
                        <td><a href="${response.img}">link</a></td><td>${response.luminosity}</td>
                        <td class="timestamp">${raw.timestamp}</td></tr>`;
                        $('#history_table  tr:first').after(new_row);
                    }
                },
                error: function(xhr) {
                    alert('Request failed!')
                }
            });
          },
      });
     });

    $('#load_file_submit').click(function(){
        var fd = new FormData();
        var files = $('#formFile')[0].files;
        fd.append('file',files[0]);
        $.ajax({
                url: "/admin",
                type: "post",
                contentType: false,
                processData: false,
                data: fd,
                success: function(response) {
                    if (response.error){
                        alert(response.error)
                    }
                    else{
                        $('#image_update').attr('src', '/static/uploads/' + response)
                    }
                }
            })
    });

    $('#new_house_submit').click(function(){
        $.ajax({
            url: "/add_house",
            type: "post",
            data: {
                "house_number": $('#new_house').val(),
                "street": $('#new_house_street').val(),
                "user": $('#add_house_owner').val()
            },
            success: function(response) {
                alert('House added!');
                location.reload();
            },
            error: function(xhr) {
                if (xhr.responseText != undefined) {
                    error_text = JSON.parse(xhr.responseText)
                    alert(error_text.error)
                    }
                else {
                    alert('Request failed!')
                }
            }
        });
    });

    $('#new_street_submit').click(function(){
        $.ajax({
            url: "/add_street",
            type: "post",
            data: {
                "street": $('#new_street').val(),
                "user": $('#current_user').val(),
                "city": $('#current_city').val(),
            },
            success: function(raw) {
                alert('Street added!');
                location.reload();
            },
            error: function(xhr) {
                if (xhr.responseText != undefined) {
                    error_text = JSON.parse(xhr.responseText)
                    alert(error_text.error)
                    }
                else {
                    alert('Request failed!')
                }
            }
        });
    });

    $('#new_city_submit').click(function(){
        $.ajax({
            url: "/add_city",
            type: "post",
            data: {
                "user": $('#current_user').val(),
                "city": $('#new_city').val(),
            },
            success: function(raw) {
                alert('City added!');
                location.reload();
            },
            error: function(xhr) {
                if (xhr.responseText != undefined) {
                    error_text = JSON.parse(xhr.responseText)
                    alert(error_text.error)
                    }
                    else {
                        alert('Request failed!')
                    }
            }
        });
    });

    $('#filter_street').change(function(){
        street = $(this).val()
        getHouse(street, '#filter_house', 'number');
    });

    $('#add_street').change(function(){
        street = $(this).val()
        getHouse(street, '#add_house', 'id');
    });

    $('#filter_city').change(function(){
        city = $(this).val()
        getStreet(city, '#filter_street', 'id');
    });

    $('#add_city').change(function(){
        city = $(this).val()
        getStreet(city, '#add_street', 'id');
    });

    $('#new_house_city').change(function(){
        city = $(this).val()
        getStreet(city, '#new_house_street', 'id');
    });

    $('.save_street_user').click(function(){
        user_id = $(this).parent().parent().find('.user_th select').first().val();
        if (user_id!='current') {
            console.log(user_id)
            street_id = $(this).parent().parent().find('.street_th input').first().val();
            $.ajax({
                url: "/change_street",
                type: "post",
                data: {
                    "user_id": user_id,
                    "street_id": street_id,
                },
                success: function(raw) {
                    alert('Owner changed!');
                    location.reload();
                },
                error: function(xhr) {
                    if (xhr.responseText != undefined) {
                    error_text = JSON.parse(xhr.responseText)
                    alert(error_text.error)
                    }
                    else {
                        alert('Request failed!')
                    }
                }
            });
        } else {
            alert('Wrong user selected')
        }
    });

    $('.save_house_user').click(function(){
        user_id = $(this).parent().parent().find('.user_select select').first().val();
        if (user_id!='current') {
            house_id = $(this).parent().parent().find('.house_th input').first().val();
            $.ajax({
                url: "/change_house",
                type: "post",
                data: {
                    "user_id": user_id,
                    "house_id": house_id,
                },
                success: function(response) {
                    alert('Owner changed!');
                    location.reload();
                },
                error: function(xhr) {
                    if (xhr.responseText != undefined) {
                        error_text = JSON.parse(xhr.responseText)
                        alert(error_text.error)
                        }
                    else {
                        alert('Request failed!')
                    }
            }
            });
        } else {
            alert('Wrong user selected')
        }
    });

    $('.save_city_user').click(function(){
        user_id = $(this).parent().parent().find('.user_select select').first().val();
        if (user_id!='current') {
            city_id = $(this).parent().parent().find('.city_td input').first().val();
            $.ajax({
                url: "/change_city",
                type: "post",
                data: {
                    "user_id": user_id,
                    "city_id": city_id,
                },
                success: function(raw) {
                    alert('Owner changed!');
                    location.reload();
                },
                error: function(xhr) {
                    if (xhr.responseText != undefined) {
                    error_text = JSON.parse(xhr.responseText)
                    alert(error_text.error)
                    }
                    else {
                        alert('Request failed!')
                    }
                }
            });
        } else {
            alert('Wrong user selected')
        }
    });
})

$("#phone").inputmask({"mask": "+3 (999) 999-9999"});