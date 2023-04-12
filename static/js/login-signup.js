// Load reCAPTCHA script asynchronously
const script = document.createElement("script");
script.src = "https://www.google.com/recaptcha/api.js?render=6LcglHklAAAAAHByD3vbfkrdYzOMsz13SE9-ic1d";
document.body.appendChild(script);

// Execute reCAPTCHA on login form submit
$("#login-form").submit(function (event) {
    event.preventDefault();
    grecaptcha.ready(function () {
        grecaptcha.execute("6LcglHklAAAAAHByD3vbfkrdYzOMsz13SE9-ic1d", { action: "login" }).then(function (token) {
            $("#g-recaptcha-response-login").val(token);
            $("#login-form").unbind("submit").submit();
        });
    });
});

// Execute reCAPTCHA on signup form submit
$("#signup-form").submit(function (event) {
    event.preventDefault();
    grecaptcha.ready(function () {
        grecaptcha.execute("6LcglHklAAAAAHByD3vbfkrdYzOMsz13SE9-ic1d", { action: "signup" }).then(function (token) {
            $("#g-recaptcha-response-signup").val(token);
            $("#signup-form").unbind("submit").submit();
        })
    });

});