jQuery(document).ready(function ($) {

    token = $(`input[name="csrfmiddlewaretoken"]`).val()

    height = $(window).height()

    if ($("nav").length) {
        height -= $("nav").outerHeight()
    }

    if ($("footer").length) {
        height -= $("footer").outerHeight()
    }

    $(".height_100").css("min-height", height)


    /* MODAL */

    $(document).on("click", ".open_modal", function () {
        openModal($(this).data("target"))
    })

    openModal = function (id) {
        $("#" + id).addClass("opened")
        $("html").addClass("modal_opened")
    }

    hideModal = function () {
        $(".modal.opened:not(.unhidable)").removeClass("opened")
        $("html").removeClass("modal_opened")
    }

    $(".close_modal").click(hideModal)

    $(document).mousedown(function (e) {
        if ($(e.target).hasClass("opened")) {
            hideModal()
        }
    })

    /* NAV */

    $("#profile_btn").click(function (e) {
        $("html").toggleClass("profile_opened")
        e.preventDefault()
    })

    let toasts = ["profile", "notifications"]

    $(document).mousedown(function (e) {
        toasts.forEach(id => {
            if ($(e.target).closest(`#${id}_menu`).length == 0 && $(e.target).closest(`#${id}_btn`).length == 0) {
                $("html").removeClass(`${id}_opened`)
            }
        })
    })

    $("#menu_icon").click(function () {
        $("html").toggleClass("menu_opened")
    })

    $("#notifications_btn").click(function () {
        $("html").toggleClass("notifications_opened")
        $.ajax({
            type: 'POST',
            data: {
                "action": "get_notifications",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                $("#notifications_menu").empty()
                if (res.notifications.length) {
                    res.notifications.forEach(element => {
                        $("#notifications_menu").append(
                            `<a href="${element.thread_url}" class="notification_item">
                                <div>${element.message}</div>
                                <div class="sec mt-15">${element.time}</div>
                            </a>`
                        )
                    })
                } else {
                    $("#notifications_menu").append(`<div class="mt ml">Уведомлений пока нет.</div>`)
                }
            }
        })
    })
})