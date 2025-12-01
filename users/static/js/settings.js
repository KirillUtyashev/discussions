jQuery(document).ready(function ($) {

    // NAME

    $("#name").on("input", function () {
        $("#update_profile_success").text("")
        $("#update_profile_error").text("")
        $("#update_profile").attr("disabled", $(this).val().trim().length == 0)
    })

    $("#update_profile").click(function () {
        new_name = $("#name").val().trim()

        $.ajax({
            type: 'POST',
            
            data: {
                "new_name": new_name,
                "action": "change_profile",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                switch (res["message"]) {
                    case "1":
                        $("#update_profile_success").text("Профиль успешно обновлен.")
                        $(".current_user_name").text(new_name)
                        $("#update_profile").attr("disabled", true)
                        break
                }
            }
        })
    })

    // EMAIL

    old_email = $("#email").val().trim()
    const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    $("#email").on("input", function () {
        $("#update_email_success").text("")
        $("#update_email_error").text("")
        n_em = $(this).val().trim()
        if (n_em.length > 0 && re.test($(this).val()) && old_email != n_em) {
            $("#update_email").attr("disabled", false)
        } else {
            $("#update_email").attr("disabled", true)
        }
    })

    $("#update_email").click(function () {
        $("#update_email_success").text("")
        $("#update_email_error").text("")
        new_email = $("#email").val()
        $.ajax({
            type: 'POST',
            
            data: {
                "new_email": new_email,
                "action": "change_email",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                switch (res["message"]) {
                    case "1":
                        $("#update_email_success").text("Эл. адрес успешно обновлен.")
                        $(".current_user_email").text(new_email)
                        $("#update_email").attr("disabled", true)
                        break
                    case "0":
                        $("#update_email_error").text("Эл. адрес уже используется.")
                        break
                }
            }
        })
    })

    $("#send_link").click(function () {
        $.ajax({
            type: 'POST',
            data: {
                "action": "send_link",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                if (res == "1") {
                    $(this).text("Ссылка была успешно отправлена").attr("disabled", true)
                }
            }
        })
    })

    /* PASSWORD */

    $("#new_password_again, #new_password, #current_password").on("input", function () {
        $("#update_password_error").text("")
        ps = get_passwords()
        dis = false
        ps.forEach(pass => {
            if (pass.length == 0) {
                dis = true
            }
        })

        if (!dis) {
            if (ps[1] != ps[2]) {
                $("#update_password_error").text("Пароли не совпадают.")
                dis = true
            } else {
                $("#update_password_error").text("")
            }
        }

        $("#change_password").attr("disabled", dis)
    })

    function get_passwords() {
        return [
            $("#current_password").val(),
            $("#new_password").val(),
            $("#new_password_again").val()
        ]
    }


    $("#change_password").click(function () {
        passwords = get_passwords()
        $.ajax({
            type: 'POST',
            
            data: {
                "old_password": passwords[0],
                "new_password1": passwords[1],
                "new_password2": passwords[2],
                "action": "change_password",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                switch (res["message"]) {
                    case "1":
                        $("#update_password_success").text("Пароль успешно обновлен.")
                        break
                    case "0":
                        $("#update_password_error").text("Неверный текущий пароль.")
                        break
                    case "2":
                        $("#update_password_error").text("Cлабый новый пароль.")
                        break
                }
            }
        })
    })

    /* UNENROLL */

    course_id = null

    $(".unenroll").click(function () {
        course_id = $(this).data("id")
        course_title = $(this).data("name")

        $("#course_title").text(course_title)
    })

    $("#exit_course").click(function () {
        
        $.ajax({
            type: 'POST',
            
            data: {
                "id": course_id,
                "action": "unenroll",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                if (res["message"] == "1") {
                    hideModal()
                    $(`.course[data-id="${course_id}"]`).remove()
                }
            }
        })
    })

    //PAYMENT

    stud_count = $("#student_count").text()
    max_stud_count = $("#max_student_count").text()

    $("#tarif_bar").css("width", stud_count * 100 / max_stud_count + "%")

    $(".toggle_renewal").click(function () {
        renewal = $(this).data("id")
        $.ajax({
            type: 'POST',
            data: {
                "renewal": renewal,
                "action": "switch_renewal",
                "csrfmiddlewaretoken": token
            },
            success: function(res) {
                
                if (res.message == "1") {
                    $(".renewal_status").attr("data-status", renewal)
                }
            }
        })
    })

     //URL FOR SECTIONS

     $(".menu_btn").click(function () {
        change_view($(this).data("section"))
    })


    change_url = function (param, val) {
        if (val) {
            window.history.replaceState(null, null, `?${param}=${val}`)
        } else {
            window.history.replaceState(null, null, window.location.pathname);
        }
    }

    change_view = function(tab) {
        $(".content section, .menu_btn").removeClass('active')
        $(`.menu_btn[data-section="${tab}"]`).addClass("active")
        $(`.content section[data-section="${tab}"]`).addClass('active')
        change_url("tab", tab)
    }

    url_string = window.location.href;
    url = new URL(url_string);

    if (tab = url.searchParams.get("tab")) {
        change_view(tab)
    } else {
        $(`.menu_btn[data-section="general"]`).addClass("active")
    }
})