// get form elements
const loginForm = $("#login-form");
const signupForm = $("#signup-form");
const loginToggle = $("#login-toggle");
const signupMessage = $("#signup-message");

// add event listeners
loginForm.on("submit", handleLogin);
signupForm.on("submit", handleSignup);
loginToggle.on("click", toggleForms);

// handle login form submission
async function handleLogin(event) {
    event.preventDefault(); // prevent default form behavior

    const username = $("#username").val();
    const password = $("#password").val();

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            body: JSON.stringify({ username, password }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Invalid username or password");
        }

        const data = await response.json();
        displayUserData(data.data);
    } catch (error) {
        displayError(error.message);
    }
}

// handle signup form submission
async function handleSignup(event) {
    event.preventDefault(); // prevent default form behavior

    const username = $("#new-username").val();
    const email = $("#new-email").val();
    const password = $("#new-password").val();
    const phone_number = $("#phone-number").val();

    try {
        const response = await fetch("/api/signup", {
            method: "PUT",
            body: JSON.stringify({ username, email, password, phone_number }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error("Failed to signup");
        }

        // display success message
        signupMessage.removeClass("hidden");
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
}

// display user data in the HTML
function displayUserData(data) {
    const userDisplay = `
    <p>Username: ${data.username}</p>
    <p>Email: ${data.email}</p>
    <p>Phone Number: ${data.phone_number}</p>
  `;
    $("#user-display").html(userDisplay);
}

// display error message in popup
function displayError(message) {
    const errorPopup = $("#error-popup");
    errorPopup.html(message);
    errorPopup.removeClass("hidden");
    setTimeout(() => {
        errorPopup.addClass("hidden");
    }, 3000);
}
