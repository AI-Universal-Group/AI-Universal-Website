// Define $buoop using object shorthand notation
const $buoop = {
    required: { e: -3, f: -3, o: -3, s: -1, c: -3 },
    insecure: true,
    unsupported: true,
    api: 2023.03,
};

// Use jQuery to load BrowserUpdate script and attach it to the body
$(function () {
    $('body').append('<script src="//browser-update.org/update.min.js"></script>');
});

// Use jQuery to update all elements with class "current-year" with the current year
$(function () {
    const currentYear = new Date().getFullYear();
    $('.current-year').text(currentYear);
});

// Use jQuery to toggle the display of the back to top button based on scroll position
$(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 20) {
            $('#backToTopBtn').fadeIn();
        } else {
            $('#backToTopBtn').fadeOut();
        }
    });

    // Use jQuery to animate scrolling to the top on click of the back to top button
    $('#backToTopBtn').click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 600);
        return false;
    });
});
