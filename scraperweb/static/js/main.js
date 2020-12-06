

$("#start").click(function() {
    console.log("start")
    let folderpath = $("#folderpath").val();
    let location = $("#rule_location").val();
    let name = $("#rule_name").val();
    const settings = {
        'scrape_folder':folderpath,
        'location_rule':location,
        'naming_rule':name
    };
    $.ajax({
        type: 'POST',
        url: '/start',
        data: JSON.stringify(settings),
        contentType: 'application/json',
        success: function (result) {
            console.log("success")
        },
        error: function () {
           console.log("error")
        }
    });
})