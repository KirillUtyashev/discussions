jQuery(document).ready(function ($) {

    function addAnswer(answer) {
        ans_temp = $("#answer_template").clone().removeAttr("id")

        fill_temp(ans_temp, answer)

        $(".thread_content").find(".answers").append(ans_temp)

        if (answer.comments) {
            populate_comments(ans_temp, answer.comments)
        }

        renderContent()
    }

    $(document).on("click", "#send_reply", function () {
        answer_form = tinymce.get(`answer_${active_thread.id}`)
        answer_body = answer_form.getContent()
        anonymous = $(".thread_content .anonymous_check").prop("checked")

        $.ajax({
            type: 'POST',
            data: {
                "body": answer_body,
                "anonymous": anonymous,
                "thread": active_thread.id,
                "action": "answer",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                addAnswer(res.answer)
                update_answer_count(active_thread.all_answers + 1)
                active_thread.all_answers += 1
                answer_form.setContent("")
            }
        })
    })

    populate_answers = function (thread) {
        //answers
        ans_count = thread.answers.length
        
        
        update_answer_count(ans_count)
        thread.answers.forEach(function (answer) {
            addAnswer(answer)
        })
        
        formID = `answer_${thread.id}`
        $(".thread_content .answer_form").attr("id", formID)

        initEditor(formID)
    }


    function update_answer_count(ans_count) {
        if (ans_count == 0) {
            $(".answers_count").hide()
            $(".no_answers").show()
        } else {
            $(".answers_count").text(ans_count + " " + answers_word(ans_count)).show()
            $(".no_answers").hide()
        }
        $(".threads li.active .answers_count_thread").text(ans_count)
    }

    function answers_word(count) {
        i = count % 10
        if (i >= 5 || i == 0) {
            return "ответов"
        } else if (i > 1) {
            return "ответа"
        }
        return "ответ"
    }
})