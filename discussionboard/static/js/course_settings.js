jQuery(document).ready(function ($) {

    $(".course_url").removeClass("hide")
    $(".course_url").attr('href', course_url)

    // NAME
    field_to_btn("course_name", "update_course_name", 2)

    $("#update_course_name").click(function () {
        new_name = $("#course_name").val().trim()

        $.ajax({
            type: 'POST',

            data: {
                "new_name": new_name,
                "action": "update_course_name",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {

                if (res["message"] == "1") {
                    $(".current_course_name").text(new_name)
                    success_message("update_course_name", "Название успешно изменено.")
                }
            }
        })
    })

    //LINK


    $(document).on("input", "#activate_link", function () {
        active = $(this).prop("checked")
        if (active) {
            $("#invite_link").removeClass('hide')
        } else {
            $("#invite_link").addClass('hide')
        }
        $.ajax({
            type: 'POST',
            data: {
                "active": active ? 1 : 0,
                "action": "activate_link",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {

            }
        })
    })

    $(".copy_link").click(function () {
        navigator.clipboard.writeText($(".invite_link").text()).then(function () {
            $(".copy_link").text("Ссылка скопирована")
            timeout = setTimeout(function () {
                $(".copy_link").text("Скопировать")
            }, 4000)
        })
    })


    //PASSWORD

    $("#open_password").click(function () {
        $(this).hide()
        $("#set_password").removeClass("hide")
        $("#course_password").val("")
    })

    field_to_btn("course_password", "update_password", 0)

    $("#update_password").click(function () {
        $.ajax({
            type: 'POST',
            data: {
                "password": $("#course_password").val(),
                "action": "set_password",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                if (res["message"] == "1") {
                    success_message("update_password", "Пароль успешно установлен.")
                }
            }
        })
    })

    //INSTRUCTOR

    field_to_btn("instructor_email", "add_instructor")

    $("#add_instructor").click(function () {
        $.ajax({
            type: 'POST',
            data: {
                "name": $("#instructor_email").val(),
                "action": "add_instructor",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                if (res["message"] == "1") {
                    success_message("add_instructor", "Инструктор добавлен.")

                    temp = $("#instructor_template .user_row").clone()
                    temp.attr("data-id", res.id)
                    temp.find(".name").text(res.name)
                    temp.find(".email").text(res.email)

                    $("#instructor_list").append(temp)
                }
            }
        })
    })

    //CATEGORIES

    field_to_btn("cat_name", "add_category")

    $("#add_category").click(function () {
        $.ajax({
            type: 'POST',
            data: {
                "name": $("#cat_name").val(),
                "action": "add_category",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                if (res["message"] == "1") {
                    
                    success_message("add_category", "Категория добавлена.")
                    $("#cat_name").val("")
                    add_category(res)
                } else if (res["message"] == "0") {
                    error_message("add_category", "Категория с таким названием уже существует.")
                }
            }
        })
    })

    function add_category(res) {
        temp = $("#cat_template").clone().removeAttr("id").removeClass("hide")

        temp.find("*[data-id]").attr("data-id", res.id)
        temp.find(".cat_name").text(res.name)

        $(".categories").append(temp)
    }

    //SUBCATEGORIES

    field_to_btn("subcat_name", "add_subcategory")

    top_cat_id = null

    $(document).on("click", ".add_subcat_modal", function () {
        top_cat_id = $(this).parents(".subcats").data("id")
        top_cat_name = $(`.cat[data-id="${top_cat_id}"]`).find(".cat_name").text()
        $("#main_cat_name").text(top_cat_name)
    })

    $("#add_subcategory").click(function () {
        $.ajax({
            type: 'POST',
            data: {
                "cat": top_cat_id,
                "name": $("#subcat_name").val(),
                "action": "add_subcategory",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                if (res["message"] == "1") {
                    success_message("add_subcategory", "Подкатегория добавлена.")
                    $("#subcat_name").val("")
                    add_subcategory(res)
                } else if (res["message"] == "0") {
                    error_message("add_subcategory", "Категория с таким названием уже существует.")
                }
            }
        })
    })

    function add_subcategory(res) {
        temp = $("#subcat_template .subcat").clone()

        temp.find("*[data-id]").attr("data-id", res.id)
        temp.find(".cat_name").text(res.name)

        $(`.subcats[data-id="${top_cat_id}"] .subcats_list`).append(temp)
    }

    //DELETE CAT

    cat_to_delete = null

    $(document).on("click", ".delete_cat", function () {
        cat = $(this).parents(".cat").eq(0)
        cat_to_delete = cat.data("id")
        cat_name = cat.find(".cat_name").text()
        $("#delete_cat_name").text(cat_name)

        $("#new_cat").empty()
        $("#main_cat_list .cat").each(function () {
            id = $(this).data("id")
            catname = $(this).find(".cat_name").text()
            if ($(this).hasClass("subcat")) {
                catname = "&nbsp;&nbsp;" + catname
            }
            if (id != cat_to_delete) {
                $("#new_cat").append(`<option value="${id}">${catname}</option>`)
            }
        })
    })

    $("#delete_category").click(function () {
        $.ajax({
            type: 'POST',
            data: {
                "cat_id": cat_to_delete,
                "new_cat_id": $("#new_cat").val(),
                "action": "delete_cat",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                if (res["message"] == "1") {
                    $(`.cat[data-id="${cat_to_delete}"], .subcats[data-id="${cat_to_delete}"]`).remove()
                    hideModal()
                }
            }
        })
    })

    //USERS MANAGEMENT

    $(document).on("click", ".delete_user", function () {
        id = $(this).parents(".user_row").data("id")
        $.ajax({
            type: 'POST',
            data: {
                "user_id": id,
                "action": "delete_user",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                if (res["message"] == "1") {
                    $(`.user_row[data-id="${id}"]`).remove()
                }
            }
        })

    })

    //HELPERS

    function field_to_btn(field_id, btn_id, minLength = 3) {
        $(`#${field_id}`).on("input", function () {
            $(`#${btn_id}_message`).text("").addClass("hide")
            $(`#${btn_id}`).attr("disabled", $(this).val().length < minLength)
        })
    }

    function success_message(btn_id, msg) {
        $(`#${btn_id}`).attr("disabled", true)
        $(`#${btn_id}_message`).text(msg).removeClass("red hide").addClass("green")
    }

    function error_message(btn_id, msg) {
        $(`#${btn_id}`).attr("disabled", true)
        $(`#${btn_id}_message`).text(msg).removeClass("green hide").addClass("red")
    }

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

    change_view = function (tab) {
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