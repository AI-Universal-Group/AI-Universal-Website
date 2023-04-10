// get form elements
const $loginForm = $("#login-form");
const $signupForm = $("#signup-form");
const $loginToggle = $("#login-toggle");
const $signupToggle = $("#signup-toggle");
const $signupMessage = $("#signup-message");
const $toggleMessageLogin = $("#toggle-message-login");
const $toggleMessageSignup = $("#toggle-message-signup");

// add event listeners
$loginForm.on("submit", handleLogin);
$signupForm.on("submit", handleSignup);
$loginToggle.on("click", toggleForms);
$signupToggle.on("click", toggleForms);

/**
 * Handle login form submission
 * @param {object} event - Form submission event object
 */
async function handleLogin(event) {
    event.preventDefault();

    const $username = $("#username");
    const $password = $("#password");

    try {
        const response = await fetch("/api/v1/user", {
            method: "POST",
            body: JSON.stringify({ username: $username.val(), password: $password.val() }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Invalid username or password");
        }

        const data = await response.json();
        displayUserData(data.data);
        window.location.replace("/");
    } catch (error) {
        displayError(error.message, "#error-popup");
    }
}

/**
 * Handle signup form submission
 * @param {object} event - Form submission event object
 */
async function handleSignup(event) {
    event.preventDefault();

    const $newUsername = $("#new-username");
    const $newEmail = $("#new-email");
    const $newPassword = $("#new-password");
    const $phoneNumber = $("#phone-number");

    try {
        const response = await fetch("/api/v1/user", {
            method: "PUT",
            body: JSON.stringify({ username: $newUsername.val(), email: $newEmail.val(), password: $newPassword.val(), phone_number: $phoneNumber.val() }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Failed to signup");
        }

        displayError("Signup successful, please sign in.", "#signup-message");
        toggleForms();
    } catch (error) {
        displayError(error.message, "#error-popup");
    }
}

// toggle between login and signup forms
function toggleForms() {
    $loginForm.toggleClass("hidden");
    $signupForm.toggleClass("hidden");
    $signupMessage.addClass("hidden");
    $toggleMessageLogin.toggleClass("hidden");
    $toggleMessageSignup.toggleClass("hidden");
}

/**
 * Display user data in the HTML
 * @param {object} data - User data object containing username, email, and phone number
 */
function displayUserData(data) {
    const userDisplay = `
    <p>Username: ${data.username}</p>
    <p>Email: ${data.email}</p>
    <p>Phone Number: ${data.phone_number}</p>
  `;
    $("#user-display").html(userDisplay);
}

/**
 * Display message in popup
 * @param {string} message - Message to display
 * @param {string} elementId - ID of the DOM element to display the message in
 */
function displayError(message, elementId) {
    const $element = $(elementId);
    $element.html(message);
    $element.removeClass("hidden");
    setTimeout(() => {
        $element.addClass("hidden");
    }, 3000);
}
