jQuery(document).ready(function ($) {

    id2emptymessage = {
        "name": "Пожалуйста, укажите своё имя",
        "surname": "Пожалуйста, укажите свою фамилию",
        "email": "Пожалуйста, укажите свою эл. почту",
        "password": "Пожалуйста, придумайте пароль",
    }


    $("#signup_form input").each(function () {
        $(this).on('keyup', function () {
            if ($(this).val().length == 0) {
                $(this).next(".error").text(id2emptymessage[$(this).attr("id")]).show()
            } else {
                $(this).next(".error").hide()
            }
            updateButton()
        })
    })

    function updateButton() {
        var error = false
        if ($("#password").val().length < 6) {
            error = true
        }
        if (!re.test($("#email").val())) {
            error = true
        }

        $("#signup_form input").each(function () {
            if ($(this).val().length == 0) {
                error = true
            }
        })
        $("#submitbtn").attr("disabled", error)
    }

    //Доп проверка для некоторых полей
    $("#password").on('keyup', function () {
        if ($(this).val().length == 0) {
            $(this).next(".error").text(id2emptymessage[$(this).attr("id")]).show()
        } else if ($("#password").val().length < 6) {
            $(this).next(".error").text("Пароль слишком короткий").show()
        } else {
            $(this).next(".error").hide()
        }
    })

    const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

    $("#email").on('keyup', function () {
        if ($(this).val().length == 0) {
            $(this).next(".error").text(id2emptymessage[$(this).attr("id")]).show()
        } else if (!re.test($(this).val())) {
            $(this).next(".error").text("Пожалуйста, укажите верный эл. адрес").show()
        } else {
            $(this).next(".error").hide()
        }
    })

    //Общая проверка
    function checkForm() {
        var error = false
        if ($("#password").val().length < 6) {
            $("#password").next(".error").text("Пароль слишком короткий").show()
            error = true
        }
        if (!re.test($("#email").val())) {
            $("#email").next(".error").text("Пожалуйста, укажите верный эл. адрес").show()
            error = true
        } else {
            $("#email").next(".error").hide()
        }

        $("#signup_form input").each(function () {
            if ($(this).val().length == 0) {
                $(this).next(".error").text(id2emptymessage[$(this).attr("id")]).show()
                error = true
            }
        })
        return !error
    }

    function result(res) {
        msg = res["message"]
        switch (msg) {
            case "1":
                $("#signup_form input").attr("disabled", true)
                $("#submitbtn").text("Загружаем профиль...")

                var url_string = window.location.href; 
                var url = new URL(url_string);
                var returnUrl = url.searchParams.get("next");

                redirect = "/dashboard/"
                if (returnUrl) {
                    redirect = returnUrl
                }

                document.location.href = redirect;
                break
            case "-1":
                alert("Заполните все поля")
                break
            case "0":
                $("#email").next(".error").text("Этот эл. адрес уже используется").show()
                break
        }
    }

    $("#submitbtn").click(function () {
        if (checkForm()) {
            data = {
                "name": $("#name").val(),
                "email": $("#email").val(),
                "password": $("#password").val(),
                "csrfmiddlewaretoken": token
            }

            $.ajax({
                type: 'POST',
                
                dataType: 'json',
                data: data,
                success: function (res) {
                    result(res)
                    msg = res["message"]
                }
            })
        }
    })
})