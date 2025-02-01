const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const otpForm = document.getElementById('otp-form');
const backupCodeForm = document.getElementById('backup-code-form');
const loginSection = document.getElementById('login-section');
const registerSection = document.getElementById('register-section');
const otpSection = document.getElementById('otp-section');
const backupCodeSection = document.getElementById('backup-code-section');
const protectedSection = document.getElementById('protected-section');
const errorMessage = document.getElementById('error-message');
const protectedMessage = document.getElementById('protected-message');
const logoutButton = document.getElementById('logout-button');
const registerLink = document.getElementById('register-link');
const loginLink = document.getElementById('login-link');
const backupCodeLink = document.getElementById('backup-code-link');
const otpLink = document.getElementById('otp-link');

let partialToken = null;
let accessToken = null;
const darkModeToggle = document.getElementById('dark-mode-toggle');

function chngText() {
  if (localStorage.getItem('darkMode') === 'true') {
    darkModeToggle.textContent = 'change theme?';
  }
  else { darkModeToggle.textContent = 'Ahh, change theme?'; }
}


function enableDarkMode(force = false) {
  const enable = force || !document.body.classList.contains('dark-mode');
  document.body.classList.toggle('dark-mode', enable);
  document.querySelector('.container').classList.toggle('dark-mode', enable);
  document.querySelectorAll('button').forEach(button => button.classList.toggle('dark-mode', enable));
  document.querySelectorAll('.setup-modal').forEach(modal => modal.classList.toggle('dark-mode', enable));
  document.querySelectorAll('.setup-modal-overlay').forEach(overlay => overlay.classList.toggle('dark-mode', enable));
  document.querySelectorAll('.qr-container').forEach(container => container.classList.toggle('dark-mode', enable));
  document.querySelectorAll('.backup-codes').forEach(codes => codes.classList.toggle('dark-mode', enable));
  document.querySelectorAll('.copy-btn').forEach(button => button.classList.toggle('dark-mode', enable));
  document.querySelectorAll('.secret-key').forEach(key => key.classList.toggle('dark-mode', enable));
  document.querySelectorAll('.step-instruction').forEach(instruction => instruction.classList.toggle('dark-mode', enable));

  localStorage.setItem('darkMode', enable ? 'true' : 'false');
}

darkModeToggle.addEventListener('click', () => {
  enableDarkMode();
  chngText();
});

// Toggle between login and register sections
registerLink.addEventListener('click', () => {
  loginSection.style.display = 'none';
  registerSection.style.display = 'block';
});

loginLink.addEventListener('click', () => {
  registerSection.style.display = 'none';
  loginSection.style.display = 'block';
});

// Toggle between OTP and backup code sections
backupCodeLink.addEventListener('click', () => {
  otpSection.style.display = 'none';
  backupCodeSection.style.display = 'block';
});

otpLink.addEventListener('click', () => {
  backupCodeSection.style.display = 'none';
  otpSection.style.display = 'block';
});

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
      showModal(data.message || 'Login failed');
    }
  } catch (error) {
    showModal('An error occurred. Please try again.');
  }
});
function checkPasswordStrength(password) {
  // Require at least 8 chars, one uppercase, one lowercase, one number
  const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
  if (!strongRegex.test(password)) {
    return false;
  }
  return true;
}
// Handle register form submission
registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('reg-username').value;
  const password = document.getElementById('reg-password').value;
  if (!checkPasswordStrength(password)) {
    showModal('Your password must be at least 8 characters long and include uppercase, lowercase, and a number.');
    return;
  }
  try {
    const response = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();
    if (response.status === 200) {
      show2FASetup(data.data);
      showModal('Registration successful. Please log in.');
        
      registerSection.style.display = 'none';
      loginSection.style.display = 'block';
    } else {
      showModal(data.message || 'Registration failed');
    }
  } catch (error) {
    showModal('An error occurred. Please try again.');
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
      protectedMessage.textContent = `Hello, user!\nLogged in successfully!`;
    } else {
      showModal(data.message || 'OTP verification failed');
    }
  } catch (error) {
    showModal('An error occurred. Please try again.');
  }
});

// Handle backup code form submission
backupCodeForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const backupCode = document.getElementById('backup-code').value;

  try {
    const response = await fetch('/verify-otp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${partialToken}`,
      },
      body: JSON.stringify({ backup_code: backupCode }),
    });

    const data = await response.json();
    if (response.status === 200) {
      accessToken = data.data.access_token;
      backupCodeSection.style.display = 'none';
      protectedSection.style.display = 'block';
      protectedMessage.textContent = `Hello, user!`;
       const a = document.createElement('a');
        a.href = '/protected';
        a.textContent = 'Click here to access protected content';
    } else {
      showModal(data.message || 'Backup code verification failed');
    }
  } catch (error) {
    showModal('An error occurred. Please try again.');
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
      showModal('Logout failed');
    }
  } catch (error) {
    showModal('An error occurred. Please try again.');
  }
});
let currentStep = 0;

function show2FASetup(data) {
  const modal = document.getElementById('setup-modal');
  const overlay = document.getElementById('setup-modal-overlay');

  document.getElementById('qr-image').src = data.qr_code_base64;
  document.getElementById('secret-key').textContent = data.otp_secret;

  const codesList = document.getElementById('backup-codes-list');
  codesList.innerHTML = data.backup_codes.map(code => `<div>${code}</div>`).join('');

  modal.style.display = 'block';
  overlay.style.display = 'block';

  // Ensure only the first step is visible
  currentStep = 0;
  updateCarousel();
}


function updateCarousel() {
  const steps = document.querySelectorAll('.carousel-step');
  steps.forEach((step, index) => {
    step.style.display = index === currentStep ? 'block' : 'none'; // Show only the current step
  });
}


function nextStep() {
  const steps = document.querySelectorAll('.carousel-step');
  if (currentStep < steps.length - 1) {
    currentStep++;
    updateCarousel();
  }
}

function prevStep() {
  if (currentStep > 0) {
    currentStep--;
    updateCarousel();
  }
}

function closeSetupModal() {
  document.getElementById('setup-modal').style.display = 'none';
  document.getElementById('setup-modal-overlay').style.display = 'none';
}

// Close modal when clicking outside
document.getElementById('setup-modal-overlay').addEventListener('click', closeSetupModal);

// Prevent modal from closing when clicking inside
document.getElementById('setup-modal').addEventListener('click', (e) => {
  e.stopPropagation();
});
function closeSetupModal() {
  document.getElementById('setup-modal').style.display = 'none';
  document.getElementById('setup-modal-overlay').style.display = 'none';
  window.location.href = '/'; // Redirect to login
}

function copySecretKey() {
  const secret = document.getElementById('secret-key').textContent;
  navigator.clipboard.writeText(secret);
  alert('Secret key copied to clipboard!');
}

function copyBackupCodes() {
  const codes = [...document.querySelectorAll('#backup-codes-list div')]
               .map(div => div.textContent).join('\n');
  navigator.clipboard.writeText(codes);
  alert('Backup codes copied to clipboard!');
}

function downloadBackupCodes() {
  const codes = [...document.querySelectorAll('#backup-codes-list div')]
               .map(div => div.textContent).join('\n');
  const blob = new Blob([codes], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'secure-login-backup-codes.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

// Display error messages
function showModal(message) {
  errorMessage.textContent = message;
  errorMessage.style.display = 'block';
  setTimeout(() => {
    errorMessage.style.display = 'none';
  }, 3000);
}
