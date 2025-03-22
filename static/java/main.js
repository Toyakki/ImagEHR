$(window).scroll(function() {
    var scroll = $(window).scrollTop();
    if (scroll >= 450) {
        $('.header').addClass("white");
    } else {
        $('.header').removeClass("white");
    }
});


window.transitionToPage = function(href) {
    document.querySelector('body').style.opacity = 0
    setTimeout(function() {
        window.location.href = href
    }, 500)
}

document.addEventListener('DOMContentLoaded', function(event) {
    document.querySelector('body').style.opacity = 1
})