/*
COPYRIGHT INFORMATION:
This code is owned by Zach Lagden. The use of this code in personal and commercial projects is strictly prohibited without express permission from the owner.
*/

/**
 * Initializes an Owl Carousel and AOS library, and refreshes AOS on window resize.
 */
$(document).ready(initiate);

function initiate() {
    initializeCarousel();
}

/**
 * Initialize the owlCarousel with the following settings:
 * items: 1
 * loop: true
 * autoplay: true
 * autoplayTimeout: 5000
 * autoplayHoverPause: true
 * nav: false
 * dots: true
 * animateOut: 'fadeOut'
 * smartSpeed: 450
 */
function initializeCarousel() {
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
}