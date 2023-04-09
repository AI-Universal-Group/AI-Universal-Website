/**
 * @copyright This code is the property of [company name]. You are strictly prohibited from using or distributing this code for personal or commercial purposes without explicit permission from [company name].
 */

// get form elements
const loginForm = $("#login-form");
const signupForm = $("#signup-form");
const loginToggle = $("#login-toggle");
const signupToggle = $("#signup-toggle");
const signupMessage = $("#signup-message");
const toggleMessageLogin = $("#toggle-message-login");
const toggleMessageSignup = $("#toggle-message-signup");

// add event listeners
loginForm.on("submit", handleLogin);
signupForm.on("submit", handleSignup);
loginToggle.on("click", toggleForms);
signupToggle.on("click", toggleForms);

/**
 * Handle login form submission
 * @param {object} event - Form submission event object
 */
async function handleLogin(event) {
    event.preventDefault(); // prevent default form behavior

    const username = $("#username").val();
    const password = $("#password").val();

    try {
        const response = await fetch("/api/v1/user", {
            method: "POST",
            body: JSON.stringify({ username, password }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Invalid username or password");
        }

        const data = await response.json();
        displayUserData(data.data);
        window.location.replace("/");
    } catch (error) {
        displayError(error.message);
    }
}

/**
 * Handle signup form submission
 * @param {object} event - Form submission event object
 */
async function handleSignup(event) {
    event.preventDefault(); // prevent default form behavior

    const username = $("#new-username").val();
    const email = $("#new-email").val();
    const password = $("#new-password").val();
    const phone_number = $("#phone-number").val();

    try {
        const response = await fetch("/api/v1/user", {
            method: "PUT",
            body: JSON.stringify({ username, email, password, phone_number }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Failed to signup");
        }

        displayError("Signup successful, please sign in.");
        toggleForms();
    } catch (error) {
        displayError(error.message);
    }
}

// toggle between login and signup forms
function toggleForms() {
    loginForm.toggleClass("hidden");
    signupForm.toggleClass("hidden");
    signupMessage.addClass("hidden");
    toggleMessageLogin.toggleClass("hidden");
    toggleMessageSignup.toggleClass("hidden");
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
 * Display error message in popup
 * @param {string} message - Error message to display
 */
function displayError(message) {
    const errorPopup = $("#error-popup");
    errorPopup.html(message);
    errorPopup.removeClass("hidden");
    setTimeout(() => {
        errorPopup.addClass("hidden");
    }, 3000);
}

/**
 * Display message in popup
 * @param {string} message - Message to display
 */
function displayError(message) {
    const errorPopup = $("#popup");
    errorPopup.html(message);
    errorPopup.removeClass("hidden");
    setTimeout(() => {
        errorPopup.addClass("hidden");
    }, 3000);
}