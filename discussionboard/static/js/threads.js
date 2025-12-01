jQuery(document).ready(function ($) {
    active_thread = null

    show_thread = function (id, obj = null) {
        $(".threads li").removeClass("active")
        $(`.threads li[data-id="${id}"]`).addClass("active")
        $("#main .thread_content").empty().append("Загрузка...")
        change_view("thread")

        if (!obj) {
            $.ajax({
                type: 'POST',
                
                data: {
                    "id": id,
                    "action": "get_thread",
                    "csrfmiddlewaretoken": token
                },
                success: function (res) {
                    if (res["message"] == "-1") {
                        change_view("idle")
                    } else {
                        populate_thread(res)
                    }
                }
            })
        } else {
            populate_thread(obj)
        }
    }

    addThread = function (thread, just_added = false) {
        temp = $("#thread_list_template li").clone()

        fill_temp(temp, thread.question)
        fill_temp(temp, thread)

        temp.attr("data-q-id", thread.question.id)
        temp.attr("data-type", thread.type)
        temp.find('.thread_cat').text(thread.category.tag).attr("data-id", thread.category.id)

        if (thread.is_pinned) {
            $(".pinned_threads_list").append(temp)
        } else {
            if (just_added) {
                first_sep = $(".main_list .separator").eq(0)
                if (first_sep) {
                    first_sep.after(temp)
                    return
                }
            }

            if (thread.week_end) {
                $(".main_list").append(`<div class="separator">${thread.week_end}</div>`)
            }

            $(".main_list").append(temp)
        }
    }


    populate_thread = function (obj) {

        thread = obj.thread
        active_thread = thread
        question = thread.question

        change_url("id", thread.id)

        temp = $("#thread_template").clone().removeAttr("id")

        fill_temp(temp, thread)

        populate_question(temp.find(".question"), question)

        $("#main .thread_content").empty().append(temp)

        populate_comments(temp.find(".question"), thread.question.comments)

        if (thread.type == "question") {
            populate_answers(thread)
        } else {
            temp.find(".no_post").remove()
        }

        renderContent()
    }

    $(document).on("click", ".threads li", function () {
        show_thread($(this).data("id"))
    })

    update_thread_list = function (res) {

        

        $(".pinned_threads_list, .main_list").empty()
        $(".load_more").hide()

        if (res.pinned_threads.threads.length) {
            $(".pinned_threads").show()

            res.pinned_threads.threads.forEach(thread => {
                addThread(thread)
            })

            if (res.pinned_threads.show_load_more) {
                $(".pinned_threads .load_more").show()
            }

        } else {
            $(".pinned_threads").hide()

            if (res.regular_threads.threads.length == 0) {
                $(".main_list").append(`<li class="text-center">Вопросов нет. Попробуйте изменить фильтр.</li>`)
            }
        }

        res.regular_threads.threads.forEach(thread => {
            addThread(thread)
        })

        if (res.regular_threads.show_load_more) {
            $(".regular_threads .load_more").show()
        }
    }

    $(document).on("click", ".load_more", function () {

        btn = $(this)
        list = btn.data("list")

        last_thread_id = $(btn.data("cont")).find(".thread_list").last().data("id")

        $.ajax({
            type: 'POST',
            
            data: {
                "last_thread_id": last_thread_id,
                "list_type": list,
                "active_cat_filter": active_cat_filter,
                "action": "load_more",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                res.threads.forEach(thread => {
                    addThread(thread)
                })

                if (!res.show_load_more) {
                    btn.hide()
                }
            }
        })
    })
})
