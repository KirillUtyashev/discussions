jQuery(document).ready(function ($) {

    initEditor("question_body_form", false)

    $(".select_cat .top_cat").eq(0).addClass("active")

    $(".select_cat .top_cat").click(function () {
        $(".select_cat .top_cat").removeClass("active")
        $(this).addClass("active")
    })

    $(".select_cat .subcat").click(function () {
        if ($(this).hasClass("active")) {
            $(this).removeClass("active")
        } else {
            $(".select_cat .subcat").removeClass("active")
            $(this).addClass("active")
        }
    })

    populate_question = function (temp, question) {
        fill_temp(temp, question)
        temp.find(".cat").text(thread.category.tag).attr("data-id", thread.category.id)
        temp.find(".question_cat").removeClass("hide")
    }

    show_creation = function () {
        change_view("create")

        $("#publish").attr("disabled", false).text("Опубликовать")
        $("#q_title").attr("disabled", false)
    }

    $(document).on("click", ".new_thread", function () {
        change_url("create", 1)
        show_creation()
    })

    $(".type_options div").click(function () {
        $(".type_options div").removeClass("active")
        $(this).addClass("active")
    })

    $("#publish").click(function () {
        if (checkFields()) {
            type = $(".type_options div.active").data("type")
            
            header = $("#q_title").val()
            body = tinymce.get("question_body_form").getContent();
            anonymous = $(".thread_creation .anonymous_check").prop("checked")

            cat = $(".select_cat .top_cat.active").data("id")
            subcat = $(`.select_cat .subcat[data-top-id="${cat}"].active`).data("id")
            if (subcat) {
                cat = subcat
            }

            $("#publish").attr("disabled", true).text("Публикуем...")
            $("#q_title").attr("disabled", true)


            $.ajax({
                type: 'POST',
                
                data: {
                    "type": type,
                    "header": header,
                    "body": body,
                    "category": cat,
                    "anonymous": anonymous,
                    "action": "post",
                    "csrfmiddlewaretoken": token
                },

                success: function (res) {
                    addThread(res.thread, true)
                    show_thread(res.thread.id, res)
                    tinymce.get("question_body_form").setContent("");
                    $("#q_title").val("")
                }
            })
        }
    })

    //CHECK

    $(document).on("input", "#q_title", function () {
        if ($("#q_title").val().trim().length > 0) {
            $("#title_error").addClass("hide")
        }
    })

    function checkFields() {
        if ($("#q_title").val().trim().length == 0) {
            $("#title_error").removeClass("hide")
            return false
        }

        body = tinymce.get("question_body_form").getContent()
        if (body.length < 20) {
            $("#body_error").removeClass("hide")
            return false
        }
        
        return true
    }

})