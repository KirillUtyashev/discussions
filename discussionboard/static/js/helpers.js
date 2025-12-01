
jQuery(document).ready(function ($) {
    
    change_view = function(view) {
        $("#main").attr("data-view", view)
        if (view == "create" || view == "idle") {
            $(".threads li").removeClass("active")
        }
    }

    get_post_id = function (el) {
        parent = $(el).parents(".post").eq(0)
        id = parent.data("id")
        return id
    }

    get_parent_cont = function (el) {
        return $(el).parents(".post").eq(0)
    }

    id_2_body = {}

    fill_temp = function (template, obj) {
        template.attr("data-id", obj.id)

        template.find(`*[data-text]`).each(function () {
            $(this).text(obj[$(this).data("text")])
        })

        template.find(`*[data-html]`).each(function () {
            $(this).html(obj[$(this).data("html")])
        })

        template.find(`*[data-attr]`).each(function () {
            $(this).attr($(this).data("attr"), obj[$(this).data("attr-value")])
        })

        template.find(`*[data-active]`).each(function () {
            if (obj[$(this).data("active")]) {
                $(this).addClass("active")
            }
        })

        template.find(`*[data-show]`).each(function () {
            if (obj[$(this).data("show")]) {
                $(this).removeClass("hide")
            }
        })

        if (is_instructor || obj.is_author) {
            template.find(".edit").removeClass("hide")
            id_2_body[obj.id] = obj.body
        }

        if (obj.is_posted_by_admin) {
            template.find(".endorse").remove()
        }
    }

    change_url = function (param, val) {
        if (val) {
            window.history.replaceState(null, null, `?${param}=${val}`)
        } else {
            window.history.replaceState(null, null, window.location.pathname);
        }
    }
})