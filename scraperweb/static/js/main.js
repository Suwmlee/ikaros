

$("#start").click(function() {
    console.log("start")

    $.ajax({
        type: 'GET',
        url: '/start',
        success: function (result) {
            console.log("success")
        },
        error: function () {
           console.log("error")
        }
    });
})