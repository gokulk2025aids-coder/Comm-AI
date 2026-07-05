const API_URL = 'http://localhost:8000/api';

// Test backend connection on page load
window.addEventListener('DOMContentLoaded', async () => {
    console.log('Testing backend connection...');
    try {
        const response = await fetch('http://localhost:8000/api/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend connected:', data);
        } else {
            console.error('❌ Backend responded with error:', response.status);
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend:', error.message);
        console.error('Make sure the backend server is running on http://localhost:8000');
    }
});

// Theme Toggle
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = themeToggle.querySelector('.theme-icon');
const savedTheme = localStorage.getItem('theme') || 'dark';

if (savedTheme === 'light') {
    document.body.setAttribute('data-theme', 'light');
    themeIcon.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.body.setAttribute('data-theme', newTheme);
    themeIcon.textContent = newTheme === 'light' ? '☀️' : '🌙';
    localStorage.setItem('theme', newTheme);
});

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.form').forEach(f => f.classList.remove('active'));
        
        tab.classList.add('active');
        
        if (tabName === 'otp') {
            document.getElementById('otp-form').classList.add('active');
        } else if (tabName === 'password') {
            document.getElementById('password-form').classList.add('active');
        } else if (tabName === 'signup') {
            document.getElementById('signup-form').classList.add('active');
        }
        
        hideMessage();
    });
});

// OTP Login
document.getElementById('otp-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('.btn');
    const email = document.getElementById('otp-email').value;
    
    console.log('OTP Request - Email:', email);
    console.log('API URL:', `${API_URL}/auth/request-otp`);
    
    btn.classList.add('loading');
    hideMessage();
    
    try {
        console.log('Sending OTP request...');
        const response = await fetch(`${API_URL}/auth/request-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok && data.success) {
            showMessage('OTP sent! Check your email or terminal.', 'success');
            document.getElementById('otp-form').style.display = 'none';
            document.getElementById('otp-verify-form').style.display = 'block';
        } else {
            const errorMsg = data.detail || data.message || 'Failed to send OTP';
            console.error('OTP request failed:', errorMsg);
            showMessage(errorMsg, 'error');
        }
    } catch (error) {
        console.error('OTP request error:', error);
        showMessage(`Network error: ${error.message}`, 'error');
    } finally {
        btn.classList.remove('loading');
    }
});

// OTP Verify
document.getElementById('otp-verify-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('.btn-primary');
    const email = document.getElementById('otp-email').value;
    const otp = document.getElementById('otp-code').value;
    
    btn.classList.add('loading');
    hideMessage();
    
    try {
        const response = await fetch(`${API_URL}/auth/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp })
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('user', JSON.stringify(data.user));
            showMessage('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/static/index.html';
            }, 1000);
        } else {
            showMessage(data.detail || 'Invalid OTP', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    } finally {
        btn.classList.remove('loading');
    }
});

// Back to email
document.getElementById('back-to-email').addEventListener('click', () => {
    document.getElementById('otp-verify-form').style.display = 'none';
    document.getElementById('otp-form').style.display = 'block';
    document.getElementById('otp-code').value = '';
    hideMessage();
});

// Password Login
document.getElementById('password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('.btn');
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    btn.classList.add('loading');
    hideMessage();
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('user', JSON.stringify(data.user));
            showMessage('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/static/index.html';
            }, 1000);
        } else {
            showMessage(data.detail || 'Invalid credentials', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    } finally {
        btn.classList.remove('loading');
    }
});

// Signup
document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('.btn');
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirm = document.getElementById('signup-confirm').value;
    
    if (password !== confirm) {
        showMessage('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters', 'error');
        return;
    }
    
    btn.classList.add('loading');
    hideMessage();
    
    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('user', JSON.stringify(data.user));
            showMessage('Account created! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = '/static/index.html';
            }, 1000);
        } else {
            showMessage(data.detail || 'Signup failed', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    } finally {
        btn.classList.remove('loading');
    }
});

function showMessage(text, type) {
    const message = document.getElementById('message');
    message.textContent = text;
    message.className = `message show ${type}`;
}

function hideMessage() {
    const message = document.getElementById('message');
    message.classList.remove('show');
}

// Modal Logic for Footer Links
const infoModal = document.getElementById('info-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const modalClose = document.getElementById('modal-close');

const modalContent = {
    about: {
        title: 'About CommAI',
        body: `
            <h4>Understand Your Inbox with CommAI</h4>
            <p>CommAI is an advanced, AI-powered communication analyzer designed to help professionals write better, more effective emails. Our platform leverages state-of-the-art Natural Language Processing (NLP) to evaluate tone, sentiment, and clarity in real-time.</p>
            <h4>Key Features</h4>
            <ul>
                <li><strong>Tone & Sentiment Analysis:</strong> Instantly know how your email sounds before you hit send.</li>
                <li><strong>Grammar & Structure Checks:</strong> Ensure your communication is always professional and error-free.</li>
                <li><strong>AI-Powered Suggestions:</strong> Get smart rewrites to improve the effectiveness of your message.</li>
                <li><strong>Multi-Language Support:</strong> Communicate confidently across borders with our comprehensive language tools.</li>
            </ul>
            <p>Our mission is to bridge communication gaps and foster better, more empathetic professional relationships through the power of AI.</p>
        `
    },
    privacy: {
        title: 'Privacy Policy',
        body: `
            <h4>Your Privacy Matters</h4>
            <p>At CommAI, we take your privacy and data security seriously. This policy outlines how we handle your information.</p>
            <h4>Data Collection</h4>
            <p>We only collect the data necessary to provide our services. When you analyze an email, the text is processed securely and is not stored permanently unless explicitly requested for your history log.</p>
            <h4>Data Usage</h4>
            <p>Your email content is used strictly for generating analysis, suggestions, and insights. We do not use your private communications to train our foundational models without explicit consent.</p>
            <h4>Security Measures</h4>
            <p>We employ industry-standard encryption and security protocols to ensure that your data remains safe during transit and processing.</p>
            <p>For full details on our data practices, please contact our privacy team.</p>
        `
    },
    terms: {
        title: 'Terms of Service',
        body: `
            <h4>Acceptance of Terms</h4>
            <p>By accessing and using CommAI, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our platform.</p>
            <h4>Use of Service</h4>
            <p>CommAI is intended for professional and personal communication enhancement. You agree not to use the service for generating spam, malicious content, or any illegal activities.</p>
            <h4>Disclaimer of Warranties</h4>
            <p>While our AI strives for high accuracy, the analysis and suggestions provided are for informational purposes. Users should always review AI-generated content before sending.</p>
            <h4>Account Security</h4>
            <p>You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.</p>
        `
    }
};

function openModal(type) {
    const content = modalContent[type];
    if (content) {
        modalTitle.innerHTML = content.title;
        modalBody.innerHTML = content.body;
        infoModal.style.display = 'flex';
        // Small delay to allow display:flex to apply before adding opacity class
        setTimeout(() => {
            infoModal.classList.add('show');
        }, 10);
    }
}

function closeModal() {
    infoModal.classList.remove('show');
    setTimeout(() => {
        infoModal.style.display = 'none';
    }, 300); // Matches CSS transition duration
}

document.getElementById('link-about').addEventListener('click', (e) => {
    e.preventDefault();
    openModal('about');
});

document.getElementById('link-privacy').addEventListener('click', (e) => {
    e.preventDefault();
    openModal('privacy');
});

document.getElementById('link-terms').addEventListener('click', (e) => {
    e.preventDefault();
    openModal('terms');
});

modalClose.addEventListener('click', closeModal);

// Close when clicking outside the modal
infoModal.addEventListener('click', (e) => {
    if (e.target === infoModal) {
        closeModal();
    }
});
