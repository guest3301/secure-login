const loginForm = document.getElementById('login-form');
const otpForm = document.getElementById('otp-form');
const loginSection = document.getElementById('login-section');
const otpSection = document.getElementById('otp-section');
const protectedSection = document.getElementById('protected-section');
const errorMessage = document.getElementById('error-message');
const protectedMessage = document.getElementById('protected-message');
const logoutButton = document.getElementById('logout-button');

let partialToken = null;
let accessToken = null;

// Handle login form submission
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const response = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    if (response.status === 403 && data.action_required === 'otp') {
      partialToken = data.partial_token;
      loginSection.style.display = 'none';
      otpSection.style.display = 'block';
    } else {
      showError(data.message || 'Login failed');
    }
  } catch (error) {
    showError('An error occurred. Please try again.');
  }
});

// Handle OTP form submission
otpForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const otp = document.getElementById('otp').value;

  try {
    const response = await fetch('/verify-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${partialToken}`,
      },
      body: JSON.stringify({ otp }),
    });

    const data = await response.json();
    if (response.status === 200) {
      accessToken = data.data.access_token;
      otpSection.style.display = 'none';
      protectedSection.style.display = 'block';
      protectedMessage.textContent = `Hello, user!`;
    } else {
      showError(data.message || 'OTP verification failed');
    }
  } catch (error) {
    showError('An error occurred. Please try again.');
  }
});

// Handle logout
logoutButton.addEventListener('click', async () => {
  try {
    const response = await fetch('/logout', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${accessToken}` },
    });

    if (response.status === 200) {
      accessToken = null;
      protectedSection.style.display = 'none';
      loginSection.style.display = 'block';
    } else {
      showError('Logout failed');
    }
  } catch (error) {
    showError('An error occurred. Please try again.');
  }
});

// Display error messages
function showError(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
  setTimeout(() => {
    errorMessage.style.display = 'none';
  }, 3000);
}