jQuery(document).ready(function ($) {

    //LIKE
    $(document).on("click", ".like_icon", function () {
        cont = $(this).parent()
        count = cont.find(".likes_count")

        cont.toggleClass("active")
        
        likes = parseInt(count.text())
        now_active = cont.hasClass("active")
        
        if (now_active) {
            likes++
        } else {
            likes--
        }

       id = get_post_id(this)

        count.text(likes)

        if ($(`li[data-q-id="${id}"]`).length) {
            thread_like = $(`li[data-q-id="${id}"] .like`)
            thread_like.find(".likes_count").text(likes)
            thread_like.toggleClass("active")
        }

        $.ajax({
            type: 'POST',
            data: {
                "id": id,
                "action": "like",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {

            }
        })
    })

    //DELETE 

    $(document).on("click", ".delete", function () {
        id = get_post_id(this)
        
        btn = this

        $.ajax({
            type: 'POST',
            
            data: {
                "id": id,
                "action": "delete",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                $(btn).parents(".post").eq(0).find(".post_body").eq(0).html("<i>Публикация удалена.</i>")
            }
        })
    })


    //PIN
    $(document).on("click", ".pin", function () {
        pin = $(this)
        $.ajax({
            type: 'POST',
            
            data: {
                "id": active_thread.id,
                "action": "pin",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                if (res["message"] == "1") {
                    pin.toggleClass("active")
                }
            }
        })
    })


    //ENDORSE
    $(document).on("click", ".endorse", function () {
        endorse_btn = $(this)
        post = get_parent_cont(endorse_btn)
        id = get_post_id(endorse_btn)

        $.ajax({
            type: 'POST',
            
            data: {
                "id": id,
                "action": "endorse",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                
                if (res["message"] == "1") {
                    endorse_btn.toggleClass("active")
                    now_endorsed = endorse_btn.hasClass("active")
                    post = get_parent_cont(endorse_btn)
                    if (now_endorsed) {
                        post.find(`*[data-active="is_endorsed"]`).eq(0).addClass("active")
                        post.find(`.bottom_actions *[data-active="is_endorsed"]`).eq(0).addClass("active")
                        post.find(`*[data-show="is_endorsed"]`).eq(0).show()
                    } else {
                        post.find(`*[data-active="is_endorsed"]`).eq(0).removeClass("active")
                        post.find(`.bottom_actions *[data-active="is_endorsed"]`).eq(0).removeClass("active")
                        post.find(`*[data-show="is_endorsed"]`).eq(0).hide()
                    }
                }
            }
        })
    })

    //EDIT

    $(document).on("click", ".edit", function () {
        edit_btn = $(this)
        post_cont = get_parent_cont(edit_btn)

        if (post_cont.hasClass("editing")) {
            return
        }

        post_cont.addClass("editing")

        id = get_post_id(edit_btn)
        body_cont = post_cont.find(".post_body").eq(0)
        
        field_id = `edit_${id}`
        
        body_cont.after(`
            <div class="edit_post">
                <textarea id="${field_id}"></textarea>
                <div class="mt alc sb">
                    <div class="sec pointer cancel_edit">Отменить</div>
                    <button class="btn update_post" data-post-id="${id}" data-field-id="${field_id}">Обновить</button>
                </div>
            </div>`).hide()
            
        initEditor(field_id)

        setTimeout(function () {
            let tiny = tinymce.get(field_id)

            tiny.setContent(id_2_body[id])
        }, 200)
    })

    $(document).on("click", ".cancel_edit", function () {
        cancel_edit(get_parent_cont(this))
    })

    function cancel_edit (post_cont) {
        tinymce.remove(`#edit_${post_cont.data("id")}`)
        post_cont.find(".post_body").eq(0).show()
        post_cont.find(".edit_post").remove()
        post_cont.removeClass("editing")
    }

    $(document).on("click", ".update_post", function () {
        post_cont = get_parent_cont(this)
        field_id = $(this).data("field-id")
        post_id = $(this).data("post-id")
        new_content = tinymce.get(field_id).getContent()

        $.ajax({
            type: 'POST',    
            data: {
                "id": post_id,
                "new_content": new_content,
                "action": "edit",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                id_2_body[post_id] = res.body
                cancel_edit(post_cont)
                post_cont.find(".post_body").eq(0).html(res.body)
                renderContent()
            }
        })
    })

})