// Scroll animation for homepage
$(document).ready(function () {
    const elementsToAnimate = $('.example-usage, .testimonial');

    function checkVisibility() {
        const windowHeight = $(window).height();
        const windowTop = $(window).scrollTop();
        const windowBottom = windowTop + windowHeight;

        elementsToAnimate.each(function () {
            const element = $(this);

            // Skip the element if it has already been animated
            if (element.hasClass('animated')) {
                return;
            }

            const elementHeight = element.outerHeight();
            const elementTop = element.offset().top;
            const elementBottom = elementTop + elementHeight;

            if (elementBottom >= windowTop && elementTop <= windowBottom) {
                element.addClass('visible animated');
            }
        });
    }

    checkVisibility();

    // Debounce the scroll event to improve performance
    let debounceTimer;
    $(window).on('scroll', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(checkVisibility, 10);
    });
});

// Initialize the testimonials carousel
$(document).ready(function () {
    $('.owl-carousel').owlCarousel({
        items: 3,
        margin: 10,
        loop: true,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplayHoverPause: true,
        nav: false,
        dots: true,
        animateOut: 'fadeOut',
        smartSpeed: 450
    })
});
