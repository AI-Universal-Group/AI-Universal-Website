function updateCurrentYearElements() {
    const currentYear = new Date().getFullYear();
    $('.current-year').text(currentYear);
}

function initBrowserUpdateScript() {
    const $buoop = {
        required: { e: -3, f: -3, o: -3, s: -1, c: -3 },
        insecure: true,
        unsupported: true,
        api: 2023.03,
    };
    $('body').append('<script defer src="//browser-update.org/update.min.js"></script>');
}

function initBackToTopBtn() {
    const $backToTopBtn = $('#backToTopBtn');
    $(window).scroll(function () {
        if ($(this).scrollTop() > 20) {
            $backToTopBtn.fadeIn();
        } else {
            $backToTopBtn.fadeOut();
        }
    });

    $backToTopBtn.click(function () {
        $('body,html').animate({
            scrollTop: 0
        }, 600);
        return false;
    });
}

function faceFlashMsgs() {
    setTimeout(function () {
        $('#flash-messages').fadeOut('slow');
    }, 2000); // 5000 milliseconds = 5 seconds
}

// Run after loading
$(document).ready(function () {
    updateCurrentYearElements();
    initBrowserUpdateScript();
    initBackToTopBtn();
    faceFlashMsgs();
});

$(document).ready(function () {
    const topLoader = $("#top-loader");
    const progress = $(".progress");

    topLoader.show();

    function startLoading() {
        progress.css("animation", "loading 1s linear infinite");
    }

    function stopLoading() {
        progress.css("animation", "none");
        progress.css("transform", "translateX(-100%)");
    }

    startLoading();

    $(window).on("load", function () {
        stopLoading();
    });
});