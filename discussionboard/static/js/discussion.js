jQuery(document).ready(function ($) {

    if (is_instructor) {
        $("html").addClass("is_instructor")
        $(".course_settings").removeClass("hide")
    }

    $(".open_cat_menu").click(function () {
        $("html").toggleClass("cat_menu_opened")
    })

    $(document).mousedown(function (e) {
        if ($(e.target).parents(".cat_bar").length == 0 && !$(e.target).hasClass("open_cat_menu")) {
            $("html").removeClass("cat_menu_opened")
            return
        }
    })

    $("#cat_menu_cover").click(function () {
        $("html").removeClass("cat_menu_opened")
    })

    $(document).on("click", ".back_to_threads", function () {
        change_url(null, null)
        change_view("idle")
    })

    //VIEW THREAD
    url_string = window.location.href;
    url = new URL(url_string);
    params = url.searchParams

    if (t_id = params.get("id")) {
        show_thread(t_id)
    } else if (create = params.get("create")) {
        show_creation()
    } else if (filter = params.get("filter")) {
        filter_by_cat(filter)
    }

    $(".course_settings").attr('href', course_settings_url)
})
