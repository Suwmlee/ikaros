

$("#start").click(function() {
    console.log("start")
    let folderpath = $("#folderpath").val();
    $.ajax({
        type: 'POST',
        url: '/start',
        data: JSON.stringify(folderpath),
        contentType: 'application/json',
        success: function (result) {
            console.log("success")
        },
        error: function () {
           console.log("error")
        }
    });
})