jQuery(document).ready(function ($) {

    //FILTER

    active_cat_filter = null

    $(".cat_bar .cat").click(function () {
        id = null
        if (!$(this).hasClass("active")) {
            id = $(this).data("id")
        }

        if ($(this).hasClass("active") && $(this).hasClass("subcat")) {
            id = $(this).data("top-id")
        }

        active_cat_filter = id

        change_url("filter", id)

        filter_by_cat(id)
    })

    filter_by_cat = function (cat_id) {
        $(".cat_bar .cat").removeClass("active")
        if (cat_id) {
            cat_btn = $(`.cat_bar .cat[data-id="${cat_id}"]`)
            cat_btn.addClass("active")
            if (cat_btn.hasClass("subcat")) {
                $(`.cat_bar .cat[data-id="${cat_btn.data("top-id")}"]`).addClass("active")
            }

        }

        $.ajax({
            type: 'POST',
            
            data: {
                "id": cat_id,
                "action": "filter",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                update_thread_list(res)
            }
        })
    }

    colors = ["blue", "green", "yellow", "turq", "orange", "red", "accent"]

    $(".cat_bar .top_cat").each(function (i, el) {
        id = $(el).data("id")
        index = i % colors.length
        
        assignColor(id, colors[index])

        $(`.cat_bar .subcat[data-top-id="${id}"]`).each(function () {
            assignColor($(this).data("id"), colors[index])
        })

    })

    function assignColor (cat_id, color) {
        $("head").append(`<style>
        .cat[data-id="${cat_id}"] {
            color: var(--${color})
        }

        .cat[data-id="${cat_id}"] .cat_square {
            background-color: var(--${color})
        }
    </style>`)
    }

})