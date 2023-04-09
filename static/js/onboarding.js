function nextStep() {
    const currentStep = $('.step.active');
    currentStep.removeClass('active');
    currentStep.next().addClass('active');
}

function finishOnboarding() {
    // Redirect the user to the dashboard or the next relevant page.
    window.location.href = '/dashboard';
}

$('#signupForm').submit(async function (event) {
    event.preventDefault();

    const username = $('#username').val();
    const password = $('#password').val();
    const email = $('#email').val();
    const phoneNumber = $('#phoneNumber').val();

    try {
        const data = await signUp(username, password, email, phoneNumber);
        console.log('Signup successful:', data);
        nextStep();
    } catch (error) {
        console.error('Signup error:', error.message);
        // Display an error message to the user.
    }
});

async function signUp(username, password, email, phoneNumber) {
    const response = await fetch('/api/v1/user', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username,
            password,
            email,
            phone_number: phoneNumber
        })
    });

    if (response.ok) {
        const data = await response.json();
        return data;
    } else {
        throw new Error(await response.text());
    }
}
