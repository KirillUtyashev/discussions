jQuery(document).ready(function ($) {

    $(".price_box").click(function () {
        $(".price_box").removeClass("active")
        $(this).addClass("active")
        updateTerms()
    })

    url_string = window.location.href;
    url = new URL(url_string);

    if (tab = url.searchParams.get("plan")) {
        $(`.price_box[data-plan="${tab}"]`).addClass("active")
        updateTerms()
    }

    function updateTerms() {
        updatePayButton()
        $("#term_price").text($(".price_box.active").data("price"))
    }

    $("#pay").click(function () {
        $.ajax({
            type: 'POST',
            data: {
                "plan": $(".price_box.active").data("plan"),
                "action": "buy",
                "csrfmiddlewaretoken": token
            },
            success: function (res) {
                if (res.url) {
                    document.location.href = res.url
                } else {
                    alert("Произошла ошибка. Пожалуйста, попробуйте позже или свяжитесь с нами.")
                }
            }
        })
    })

    $(".mandatory").on("input", updatePayButton)

    function updatePayButton () {
        if ($(".price_box.active").hasClass("current_plan")) {
            $("#pay").attr("disabled", true).text("Это ваш текущий тариф")
            return
        }
        $("#pay").text("Оплатить")
        
        if ($(`.mandatory:checked`).length == 2 && $(".price_box.active").length != 0) {
            $("#pay").attr("disabled", false)
        } else {
            $("#pay").attr("disabled", true)
        }
    }

    
})