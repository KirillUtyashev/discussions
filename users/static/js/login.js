jQuery(document).ready(function ($) {

    let url_string = window.location.href;
    let url = new URL(url_string);
    let returnUrl = url.searchParams.get("next");

    if (returnUrl) {
        $("#register_url").attr("href", `/register?next=${returnUrl}`)
    }

    id2emptymessage = { "email": "Пожалуйста, укажите свою эл. почту", "password": "Пожалуйста, укажите пароль", }

    $(window).keydown(function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    //Проверка на пустоту
    $("#login_form input").on('blur input change', function () {
        if ($(this).val().length == 0) {
            $(this).next(".error").text(id2emptymessage[$(this).attr("id")]).show()
        } else {
            $(".general").hide()
            $(this).next(".error").hide()
        }
        updateButton()
    })

    $("#email_reset").on('blur input change', function () {
        if ($(this).val().length == 0) {
            $("#resetbtn").attr("disabled", true)
        } else {
            $("#resetbtn").attr("disabled", false)
        }
    })

    //Общая проверка
    function checkForm() {
        var error = false
        $("#login_form input").each(function () {
            if ($(this).val().length == 0) {
                $(this).next(".error").text(id2emptymessage[$(this).attr("id")]).show()
                error = true
            }
        })
        $("#submitbtn").attr("disabled", error)
        return !error
    }

    function updateButton() {
        var error = false
        $("#login_form input").each(function () {
            if ($(this).val().length == 0) {
                error = true
            }
        })
        $("#submitbtn").attr("disabled", error)
    }

    updateButton();

    function result(res) {

        msg = res["message"]
        switch (msg) {
            case "1":
                $("#login_form input").attr("disabled", true)
                $("#submitbtn").text("Загружаем профиль...")

                redirect = "/dashboard/"
                if (returnUrl) {
                    redirect = returnUrl
                }

                document.location.href = redirect;
                break
            case "0":
                $(".general").text("Неверные данные").show()
                break
            case "2":
                $(".general").text("Логин или эл. почта не зарегистрированы").show()
                break
            case "3":
                $(".general").text('Войдите через соц. сеть или нажмите "Забыли пароль?"').show()
                break
        }
    }

    function resetresult(res) {

        msg = res["message"]
        switch (msg) {
            case "1":
                $("html").addClass("reset-success")
                break
            case "0":
                $("#reset_form .error").text("Логин или эл. почта не зарегистрированы").show()
                break
            case "2":
                $("#reset_form .error").text("К вашему аккаунту не привязана эл. почта. Необходимо сбросить пароль через родительский или учительский аккаунт.").show()
                break
            case "3":
                $("#reset_form .error").text("Вероятно, это наша проблема с отправкой Вам письма. Пожалуйста, обратитесь в поддержку.").show()
                break
        }
    }

    $("#submitbtn").click(function () {
        if (checkForm()) {
            data = {
                "email": $("#email").val(),
                "password": $("#password").val(),
                "action": "login",
                "csrfmiddlewaretoken": token
            }

            $.ajax({
                type: 'POST',
                dataType: 'json',
                data: data,
                success: function (res) {
                    result(res)
                }
            })
        }
    })

    $("#resetbtn").click(function () {
        if ($("#email_reset").val().length > 0) {
            $(this).attr("disabled", true)
            $.ajax({
                type: 'POST',
                data: {
                    "email": $("#email_reset").val(),
                    "action": "reset",
                    "csrfmiddlewaretoken": token
                },
                success: function (res) {
                    resetresult(res)
                }
            })
        }
    })

    $(".toggle-reset").click(function () {
        $("html").toggleClass("reset")
        $("html").removeClass("reset-success")
    })
})
