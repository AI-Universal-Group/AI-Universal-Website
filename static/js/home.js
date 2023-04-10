$(document).ready(() => {
    $('.owl-carousel').owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplayHoverPause: true,
        nav: false,
        dots: true,
        animateOut: 'fadeOut',
        smartSpeed: 450
    });

    AOS.init();

    window.addEventListener('resize', function () {
        AOS.refresh();
    });
});
