jQuery(document).ready(function ($) {

    $(document).on("click", ".leave_comment", function () {
        post = $(this).parents(".post").eq(0)
        if (!$(post).hasClass("comment_opened")) {
            $(".comment_opened").removeClass("comment_opened")
            $(post).addClass("comment_opened")
            post_id = post.data("id")
            comment_id = `comment_${post_id}`


            temp = $("#comment_form_template").clone().removeAttr("id")
            temp.find(".comment_body").attr("id", comment_id)

            post.find(".comments").prepend(temp)

            initEditor(comment_id)
        }
    })

    $(document).on("click", ".cancel_comment", function () {
        post = $(this).parents(".post").eq(0)
        remove_comment_form(post)
    })

    function remove_comment_form(post) {
        post.removeClass("comment_opened")
        post.find(".comment_form").remove()
    }

    $(document).on("click", ".send_comment", function () {

        id = get_post_id(this)


        comment_form = $(this).parents(".comment_form").eq(0)
        comment_tiny = tinymce.get(`comment_${id}`)
        comment_body = comment_tiny.getContent()

        anonymous = $(comment_form).find(".anonymous_check").prop("checked")
        comments_cont = $(this).parents(".post").eq(0).find(".comments").eq(0)

        $.ajax({
            type: 'POST',
            
            data: {
                "body": comment_body,
                "target_id": id,
                "thread_id": active_thread.id,
                "action": "comment",
                "anonymous": anonymous,
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                if (res["message"] == "1") {
                    add_comment(comments_cont, res["comment"])
                    remove_comment_form(post)
                    comment_tiny.setContent("")
                }
            }
        })
    })

    populate_comments = function (post_container, comments) {
        com_cont = post_container.find(".comments").eq(0)

        comments.forEach(function (comment) {
            add_comment(com_cont, comment)
        })
    }

    function add_comment(container, comment) {
        com_temp = $("#comment_template").clone().removeAttr("id")

        fill_temp(com_temp, comment)

        container.prepend(com_temp)

        renderContent()

        if (comment.comments) {
            populate_comments(com_temp, comment.comments)
        }
    }

})