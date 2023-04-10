$(document).ready(() => {
    /* Initialize AOS */
    AOS.init();

    /* Refresh AOS on window resize */
    window.addEventListener('resize', function () {
        AOS.refresh();
    });
});
