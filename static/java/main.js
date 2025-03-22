$(window).scroll(function() {
    var scroll = $(window).scrollTop();
    if (scroll >= 450) {
        $('.header').addClass("white");
    } else {
        $('.header').removeClass("white");
    }
});