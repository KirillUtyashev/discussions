jQuery(document).ready(function ($) {


    stud_count = $("#student_count").text()
    max_stud_count = $("#max_student_count").text()

    $("#tarif_bar").css("width", stud_count * 100 / max_stud_count + "%")

    $("#code").on("input", function () {
        $("#join").attr("disabled", $(this).val().trim().length == 0)
        $("#need_password").hide()
        $("#join_error").hide()
    })

    $("#join").click(function () {

        code = $("#code").val()

        data = {
            "code": code,
            "password": $("#course_password").val(),
            "action": "join",
            "csrfmiddlewaretoken": token
        }

        $.ajax({
            type: 'POST',
            dataType: 'json',
            data: data,
            success: function (res) {

                msg = res["message"]

                switch (msg) {
                    case "0":
                        $("#join_error").text("Курса не существует. Пожалуйста, проверьте код.").show()
                        break
                    case "1":
                        document.location.href = res["course_url"]
                        break
                    case "2":
                        $("#need_password").show()
                        break
                    case "3":
                        $("#join_error").text("Вы являетесь куратором курса.").show()
                        break
                    case "4":
                        $("#join_error").text("Курс уже добавлен.").show()
                        break
                    case "5":
                        $("#join_error").text("Неверный пароль.").show()
                        break
                    case "6":
                        $("#join_error").text("У преподавателя превышен лимит количества студентов по тарифу.").show()
                        break
                }
            }
        })
    })

    $("#name").on("input", function () {
        $("#create").attr("disabled", $(this).val().trim().length == 0)
        $("#create_error").text("").hide()
    })


    $("#create").click(function () {
        data = {
            "name": $("#name").val(),
            "action": "create",
            "csrfmiddlewaretoken": token
        }

        $.ajax({
            type: 'POST',

            dataType: 'json',
            data: data,
            success: function (res) {
                
                if (res["message"] == "1") {
                    $("#name").val("")
                    $("#create").attr("disabled", true).text("Перенаправляем на курс...")
                    document.location.href = res["course_url"]
                } else if (res["message"] == "0") {
                    $("#create_error").text("У вас уже есть курс с таким названием.").show()
                }
            }
        })
    })

})
