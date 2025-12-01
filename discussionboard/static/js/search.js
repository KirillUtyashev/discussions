jQuery(document).ready(function ($) {

    active_query = null
    timer = null

    // $("#search_field").val("Вопрос 5")

    $("#search_results, #looking").hide()

    $(document).on("input", "#search_field", function () {
        query = $(this).val()

        $("#search_field_2").val(query).focus()

        openModal("search_modal")
    })

    $(document).on("input", "#search_field_2", function () {
        query = $(this).val()

        $("#search_field").val(query)

        $("#search_results, #looking").hide()

        clearTimeout(timer)

        timer = setTimeout(function () {
            if (query.length > 3) {
                $("#looking").show()

                $.ajax({
                    type: 'POST',
                    
                    data: {
                        "query": query,
                        "action": "search",
                        "csrfmiddlewaretoken": token
                    },
                    success: function (res) {
                        active_query = query
                        populate_search_results(res)
                    }
                })
            }
        }, 500)
    })

    function populate_search_results(res) {
        
        $("#looking").hide()
        $("#search_results").show()
        $("#search_list").empty()

        if (res.threads.length) {
            res.threads.forEach(thread => {
                appendThread(thread)
            })
        } else {
            $("#search_results").append("Поиск не дал результатов.")
        }

        if (res.show_load_more) {
            $("#search_load_more").show()
        } else {
            $("#search_load_more").hide()
        }
    }

    function appendThread(thread) {
        temp = $("#result_template").clone().removeAttr("id")

        temp.find('.thread_cat').text(thread.category.tag)
        fill_temp(temp, thread.question)
        fill_temp(temp, thread)

        $("#excerpt_cont").html(thread.question.body)
        excerpt = $("#excerpt_cont").text()

        temp.find('.search_excerpt').text(excerpt)

        $("#search_list").append(temp)
    }

    $(document).on("click", ".search_thread_cont", function () {
        hideModal()
        show_thread($(this).data("id"))
    })

    $("#search_load_more").click(function () {
        btn = $(this)
        last_thread_id = $("#search_list .search_thread_cont").last().data("id")

        $.ajax({
            type: 'POST',
            
            data: {
                "last_thread_id": last_thread_id,
                "search_string": active_query,
                "action": "load_more",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                res.threads.forEach(thread => {
                    appendThread(thread)
                })

                if (!res.show_load_more) {
                    btn.hide()
                }
            }
        })
    })

})