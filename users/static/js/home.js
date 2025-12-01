jQuery(document).ready(function ($) {

    $(".student_or_teacher div").click(function () {
        $(".student_or_teacher div").removeClass("active")
        $(this).addClass("active")

        $("#for_student, #for_teacher").addClass("hide")
        $(`#for_${$(this).data("choice")}`).removeClass("hide")
    })
})