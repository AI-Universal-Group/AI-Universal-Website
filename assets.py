from flask_assets import Bundle

#! JavaScript

# Define a base bundle with all the common files
base_js = Bundle(
    "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.4/jquery.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/smoothscroll/1.4.10/SmoothScroll.min.js",
    "js/base.js",
    output="gen/base.js",
    filters="jsmin",
)

# Home javascript bundle depends on the base bundle
home_js = Bundle(
    base_js,
    "https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js",
    "js/home.js",
    output="gen/home.js",
    filters="jsmin",
)

# Learn more javascript bundle depends on the base bundle
learn_more_js = Bundle(
    base_js,
    "https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js",
    "js/learn_more.js",
    output="gen/learn_more.js",
    filters="jsmin",
)

# Login/signup javascript bundle depends on the base bundle
login_signup_js = Bundle(
    base_js,
    "js/login-signup.js",
    output="gen/login_signup.js",
    filters="jsmin",
)

# Onboarding javascript bundle depends on the base bundle
onboarding_js = Bundle(
    base_js,
    "js/onboarding.js",
    output="gen/onboarding.js",
    filters="jsmin",
)

# Credits javascript bundle depends on the base bundle
credits_js = Bundle(
    base_js,
    "js/credits.js",
    output="gen/credits.js",
    filters="jsmin",
)


#! CSS

# Define a base bundle with all the common files
base_css = Bundle(
    "css/base.css",
    output="gen/base.css",
    filters="cssmin",
)

# Home CSS bundle depends on the base bundle
home_css = Bundle(
    base_css,
    "https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/assets/owl.carousel.css",
    "https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/assets/owl.theme.default.css",
    "css/home.css",
    output="gen/home.css",
    filters="cssmin",
)

# Learn more CSS bundle depends on the base bundle
learn_more_css = Bundle(
    base_css,
    "https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css",
    "css/learn_more.css",
    output="gen/learn_more.css",
    filters="cssmin",
)

# Login/signup CSS bundle depends on the base bundle
login_signup_css = Bundle(
    base_css,
    "css/login-signup.css",
    output="gen/login_signup.css",
    filters="cssmin",
)

# Onboarding CSS bundle depends on the base bundle
onboarding_css = Bundle(
    base_css,
    "css/onboarding.css",
    output="gen/onboarding.css",
    filters="cssmin",
)

# Credits CSS bundle depends on the base bundle
credits_css = Bundle(
    base_css,
    "css/credits.css",
    output="gen/credits.css",
    filters="cssmin",
)
