$('.col-md-4').hover(function() {
    $(this).addClass('hover');
}, function() {
    $(this).removeClass('hover');
});

$(document).ready(function(){
    $("a#editp").click(function(){
        $("td").toggle();
    });
});

