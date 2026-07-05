const API_URL = 'http://localhost:8000/api';
let currentUser = null;
let currentAnalysis = null;
let currentEmailText = null;
let historyCache = null;
let historyCacheTime = 0;
const CACHE_DURATION = 30000; // 30 seconds

// Custom Toast Notification System overriding native alert
window.showToast = function(message, type = 'error') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.custom-toast');
    existingToasts.forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `custom-toast toast-${type}`;
    
    // Determine colors
    let bg = '#ef4444'; // default error red
    let icon = '⚠️';
    if (type === 'success') { bg = '#22c55e'; icon = '✅'; }
    if (type === 'info') { bg = '#3b82f6'; icon = 'ℹ️'; }
    if (type === 'warning') { bg = '#eab308'; icon = '⚠️'; }

    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: ${bg};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        z-index: 999999;
        font-family: inherit;
        font-size: 15px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    `;
    
    toast.innerHTML = `<span style="font-size: 18px;">${icon}</span><span>${message}</span>`;
    document.body.appendChild(toast);
    
    // Trigger reflow
    toast.offsetHeight;
    
    // Animate in
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
    
    // Animate out after 3.5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(30px)';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
};

// Override the ugly browser alert!
window.alert = function(message) {
    window.showToast(message, 'error');
};

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
    
    // Regenerate charts with new theme colors
    if (currentAnalysis && window.radarChart) {
        generateCharts(currentAnalysis);
    }
});

// Check authentication
window.addEventListener('DOMContentLoaded', () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = '/static/login.html';
        return;
    }
    
    currentUser = JSON.parse(userStr);
    document.getElementById('user-email').textContent = currentUser.email;
    
    loadHistory();
});

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const view = item.dataset.view;
        
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        
        item.classList.add('active');
        document.getElementById(`${view}-view`).classList.add('active');
        
        if (view === 'history') {
            loadHistory();
        }
    });
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
    document.getElementById('logout-modal').style.display = 'flex';
});

document.getElementById('logout-modal-close').addEventListener('click', () => {
    document.getElementById('logout-modal').style.display = 'none';
});

document.getElementById('cancel-logout-btn').addEventListener('click', () => {
    document.getElementById('logout-modal').style.display = 'none';
});

document.getElementById('confirm-logout-btn').addEventListener('click', () => {
    localStorage.removeItem('user');
    window.location.href = '/static/login.html';
});

// Analyze Email
document.getElementById('analyze-btn').addEventListener('click', async () => {
    const btn = document.getElementById('analyze-btn');
    const emailText = document.getElementById('email-input').value.trim();
    
    if (!emailText) {
        alert('Please enter an email to analyze');
        return;
    }
    
    if (emailText.length < 10) {
        alert('Email text is too short. Please enter at least 10 characters.');
        return;
    }
    
    btn.classList.add('loading');
    btn.disabled = true;
    currentEmailText = emailText;
    
    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_text: emailText,
                user_id: currentUser.id
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.analysis) {
            currentAnalysis = data.analysis;
            displayResults(data.analysis);
            // Clear history cache to force refresh
            historyCache = null;
        } else {
            alert('Analysis failed. Please try again.');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Failed to analyze email. Please check your connection and try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

function displayResults(analysis) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';
    
    // Summary
    document.getElementById('result-summary').textContent = analysis.summary;
    
    // Tone
    document.getElementById('result-tone').textContent = analysis.tone;
    document.getElementById('result-tone-reasoning').textContent = analysis.tone_reasoning;
    
    // Detailed Tone Analysis
    if (analysis.tone_analysis) {
        document.getElementById('result-tone-analysis').textContent = analysis.tone_analysis;
    }
    
    // Intent
    document.getElementById('result-intent').textContent = analysis.intent;
    document.getElementById('result-confidence').textContent = `Confidence: ${analysis.confidence}`;
    const confidence = parseInt(analysis.confidence);
    document.getElementById('confidence-fill').style.width = `${confidence}%`;
    
    // Sentiment
    document.getElementById('result-sentiment').textContent = analysis.sentiment;
    document.getElementById('result-polarity').textContent = analysis.polarity;
    
    const polarity = parseFloat(analysis.polarity);
    const polarityPercent = ((polarity + 1) / 2) * 100;
    document.getElementById('polarity-indicator').style.left = `calc(${polarityPercent}% - 8px)`;
    
    // Emotion
    document.getElementById('result-emotion').textContent = analysis.emotion;
    
    // Priority
    const priorityEl = document.getElementById('result-priority');
    priorityEl.textContent = analysis.priority;
    priorityEl.className = 'metric-value priority-badge';
    
    const priorityColors = {
        'Critical': 'background: #fee2e2; color: #dc2626;',
        'High': 'background: #fed7aa; color: #ea580c;',
        'Medium': 'background: #fef3c7; color: #ca8a04;',
        'Low': 'background: #dcfce7; color: #16a34a;'
    };
    priorityEl.style.cssText = priorityColors[analysis.priority] || '';
    
    document.getElementById('result-priority-reason').textContent = analysis.priority_reason;
    
    // Professionalism Score
    if (analysis.professionalism_score) {
        const scoreEl = document.getElementById('result-professionalism-score');
        scoreEl.textContent = `${analysis.professionalism_score}/10`;
        
        // Color code the score
        const score = parseInt(analysis.professionalism_score);
        if (score >= 8) {
            scoreEl.style.color = '#16a34a';
        } else if (score >= 6) {
            scoreEl.style.color = '#ca8a04';
        } else if (score >= 4) {
            scoreEl.style.color = '#ea580c';
        } else {
            scoreEl.style.color = '#dc2626';
        }
        
        const reasonEl = document.getElementById('result-professionalism-reason');
        if (score >= 8) {
            reasonEl.textContent = 'Highly professional communication';
        } else if (score >= 6) {
            reasonEl.textContent = 'Acceptable but could be improved';
        } else if (score >= 4) {
            reasonEl.textContent = 'Needs significant improvement';
        } else {
            reasonEl.textContent = 'Unprofessional - requires complete rewrite';
        }
    }
    
    // Structure Analysis
    if (analysis.structure_analysis) {
        document.getElementById('result-structure-analysis').textContent = analysis.structure_analysis;
    }
    
    // Key Problems
    const problemsList = document.getElementById('result-key-problems');
    problemsList.innerHTML = '';
    if (analysis.key_problems && analysis.key_problems.length > 0) {
        analysis.key_problems.forEach(problem => {
            const li = document.createElement('li');
            li.textContent = problem;
            li.style.color = problem.includes('No major issues') ? '#16a34a' : 'inherit';
            problemsList.appendChild(li);
        });
    }
    
    // Suggestions
    const suggestionsList = document.getElementById('result-suggestions');
    suggestionsList.innerHTML = '';
    if (analysis.suggestions && analysis.suggestions.length > 0) {
        analysis.suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            suggestionsList.appendChild(li);
        });
    }
    
    // Key Points
    const keyPointsList = document.getElementById('result-key-points');
    keyPointsList.innerHTML = '';
    if (analysis.key_points && analysis.key_points.length > 0) {
        analysis.key_points.forEach(point => {
            const li = document.createElement('li');
            li.textContent = point;
            keyPointsList.appendChild(li);
        });
    }
    
    // Action Items
    const actionItemsEl = document.getElementById('result-action-items');
    actionItemsEl.innerHTML = '';
    
    if (!analysis.action_items || analysis.action_items.length === 0) {
        actionItemsEl.innerHTML = '<p style="color: #6b7280;">No specific action items identified</p>';
    } else {
        analysis.action_items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'action-item';
            div.innerHTML = `
                <div class="action-item-text">${item.action}</div>
                <div class="action-item-responsibility">Responsibility: ${item.responsibility}</div>
            `;
            actionItemsEl.appendChild(div);
        });
    }
    
    // Email Suggestion
    document.getElementById('result-email-suggestion').textContent = analysis.email_suggestion || 'No suggestion available';
    
    // Suggested Reply
    document.getElementById('result-reply').textContent = analysis.suggested_reply || 'No reply suggestion available';
    
    // Email Scoring System
    if (analysis.email_scores) {
        displayEmailScores(analysis.email_scores);
    }
    
    // Generate Charts
    setTimeout(() => {
        generateCharts(analysis);
    }, 100);
}

function displayEmailScores(scores) {
    // Overall Score with circular progress
    const overallScore = scores.overall_score || 0;
    const overallCircle = document.getElementById('overall-score-circle');
    const overallValue = document.getElementById('overall-score-value');
    const overallDesc = document.getElementById('overall-score-desc');
    
    overallValue.textContent = overallScore;
    overallCircle.style.setProperty('--score-percent', `${overallScore}%`);
    
    // Color code and description based on score
    if (overallScore >= 80) {
        overallCircle.style.background = `conic-gradient(from 0deg, #22c55e 0%, #16a34a ${overallScore}%, var(--input-bg) ${overallScore}%)`;
        overallDesc.textContent = 'Excellent Quality';
        overallDesc.style.color = '#22c55e';
    } else if (overallScore >= 60) {
        overallCircle.style.background = `conic-gradient(from 0deg, #667eea 0%, #764ba2 ${overallScore}%, var(--input-bg) ${overallScore}%)`;
        overallDesc.textContent = 'Good Quality';
        overallDesc.style.color = '#667eea';
    } else if (overallScore >= 40) {
        overallCircle.style.background = `conic-gradient(from 0deg, #eab308 0%, #ca8a04 ${overallScore}%, var(--input-bg) ${overallScore}%)`;
        overallDesc.textContent = 'Needs Improvement';
        overallDesc.style.color = '#eab308';
    } else {
        overallCircle.style.background = `conic-gradient(from 0deg, #ef4444 0%, #dc2626 ${overallScore}%, var(--input-bg) ${overallScore}%)`;
        overallDesc.textContent = 'Poor Quality';
        overallDesc.style.color = '#ef4444';
    }
    
    // Readability Score
    const readabilityScore = scores.readability_score || 0;
    document.getElementById('readability-score').textContent = `${readabilityScore}/100`;
    document.getElementById('readability-bar').style.width = `${readabilityScore}%`;
    setScoreBarColor('readability-bar', readabilityScore);
    
    // Clarity Score
    const clarityScore = scores.clarity_score || 0;
    document.getElementById('clarity-score').textContent = `${clarityScore}/100`;
    document.getElementById('clarity-bar').style.width = `${clarityScore}%`;
    setScoreBarColor('clarity-bar', clarityScore);
    
    // Engagement Score
    const engagementScore = scores.engagement_score || 0;
    document.getElementById('engagement-score').textContent = `${engagementScore}/100`;
    document.getElementById('engagement-bar').style.width = `${engagementScore}%`;
    setScoreBarColor('engagement-bar', engagementScore);
    
    // Professional Impact Score
    const impactScore = scores.professional_impact_score || 0;
    document.getElementById('impact-score').textContent = `${impactScore}/100`;
    document.getElementById('impact-bar').style.width = `${impactScore}%`;
    setScoreBarColor('impact-bar', impactScore);
}

function setScoreBarColor(barId, score) {
    const bar = document.getElementById(barId);
    if (score >= 80) {
        bar.style.background = 'linear-gradient(90deg, #22c55e 0%, #16a34a 100%)';
    } else if (score >= 60) {
        bar.style.background = 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)';
    } else if (score >= 40) {
        bar.style.background = 'linear-gradient(90deg, #eab308 0%, #ca8a04 100%)';
    } else {
        bar.style.background = 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
    }
}

function generateCharts(analysis) {
    console.log('=== CHART GENERATION START ===');
    console.log('Analysis data:', analysis);
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js is NOT loaded!');
        document.querySelectorAll('.chart-box').forEach(box => {
            box.innerHTML = '<p style="color: red; text-align: center; padding: 20px;">⚠️ Chart.js library failed to load.<br>Please refresh the page or check your internet connection.</p>';
        });
        return;
    }
    
    console.log('✅ Chart.js is loaded, version:', Chart.version);
    
    // Destroy existing charts if they exist
    if (window.radarChart) {
        console.log('Destroying existing radar chart');
        try {
            window.radarChart.destroy();
        } catch (e) {
            console.warn('Error destroying radar chart:', e);
        }
    }
    if (window.barChart) {
        console.log('Destroying existing bar chart');
        try {
            window.barChart.destroy();
        } catch (e) {
            console.warn('Error destroying bar chart:', e);
        }
    }
    if (window.pieChart) {
        console.log('Destroying existing pie chart');
        try {
            window.pieChart.destroy();
        } catch (e) {
            console.warn('Error destroying pie chart:', e);
        }
    }
    
    // Get theme colors
    const isDark = document.body.getAttribute('data-theme') !== 'light';
    const textColor = isDark ? '#ffffff' : '#1f2937';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    console.log('Theme:', isDark ? 'dark' : 'light');
    
    // 1. Radar Chart - Sentiment & Tone Overview
    const radarCanvas = document.getElementById('radarChart');
    if (!radarCanvas) {
        console.error('Radar chart canvas not found!');
        return;
    }
    console.log('Radar canvas found:', radarCanvas);
    
    const radarCtx = radarCanvas.getContext('2d');
    if (!radarCtx) {
        console.error('Could not get 2D context for radar chart');
        return;
    }
    
    // Calculate scores
    const polarityScore = ((parseFloat(analysis.polarity) + 1) / 2) * 100;
    const confidenceScore = parseInt(analysis.confidence);
    const subjectivityScore = (parseFloat(analysis.subjectivity) || 0.5) * 100;
    
    const toneScores = {
        'Formal': 90,
        'Friendly': 75,
        'Neutral': 50,
        'Negative': 30,
        'Apologetic': 60
    };
    const toneScore = toneScores[analysis.tone] || 50;
    
    const sentimentScores = {
        'Positive': 85,
        'Neutral': 50,
        'Negative': 20
    };
    const sentimentScore = sentimentScores[analysis.sentiment] || 50;
    
    console.log('Radar chart scores:', { sentimentScore, confidenceScore, toneScore, polarityScore, subjectivityScore });
    
    try {
        window.radarChart = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Sentiment', 'Confidence', 'Tone Quality', 'Polarity', 'Clarity'],
                datasets: [{
                    label: 'Email Metrics',
                    data: [sentimentScore, confidenceScore, toneScore, polarityScore, subjectivityScore],
                    backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgb(99, 102, 241)',
                    pointBorderColor: '#fff',
                    pointRadius: 6,
                    pointHoverRadius: 9,
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(99, 102, 241)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: textColor,
                            backdropColor: 'transparent',
                            font: { size: 13 },
                            stepSize: 20
                        },
                        grid: { color: gridColor },
                        pointLabels: {
                            color: textColor,
                            font: { size: 14, weight: 'bold' }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: { color: textColor, font: { size: 14 } }
                    }
                }
            }
        });
        console.log('Radar chart created successfully');
    } catch (error) {
        console.error('Error creating radar chart:', error);
    }
    
    // 2. Bar Chart - Analysis Scores
    const barCanvas = document.getElementById('barChart');
    if (!barCanvas) {
        console.error('Bar chart canvas not found!');
        return;
    }
    console.log('Bar canvas found:', barCanvas);
    
    const barCtx = barCanvas.getContext('2d');
    
    try {
        window.barChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: ['Sentiment', 'Confidence', 'Tone', 'Polarity'],
                datasets: [{
                    label: 'Score (%)',
                    data: [sentimentScore, confidenceScore, toneScore, polarityScore],
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(168, 85, 247, 0.8)',
                        'rgba(236, 72, 153, 0.8)'
                    ],
                    borderColor: [
                        'rgb(34, 197, 94)',
                        'rgb(99, 102, 241)',
                        'rgb(168, 85, 247)',
                        'rgb(236, 72, 153)'
                    ],
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: textColor, font: { size: 13 } },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor, font: { size: 14, weight: 'bold' } },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: { color: textColor, font: { size: 14 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` ${ctx.parsed.y}%`
                        }
                    }
                }
            }
        });
        console.log('Bar chart created successfully');
    } catch (error) {
        console.error('Error creating bar chart:', error);
    }
    
    // 3. Pie Chart - Priority Distribution
    const pieCanvas = document.getElementById('pieChart');
    if (!pieCanvas) {
        console.error('Pie chart canvas not found!');
        return;
    }
    console.log('Pie canvas found:', pieCanvas);
    
    const pieCtx = pieCanvas.getContext('2d');
    
    const priorityWeights = {
        'Critical': [90, 5, 3, 2],
        'High': [20, 60, 15, 5],
        'Medium': [10, 20, 50, 20],
        'Low': [5, 10, 20, 65]
    };
    
    const weights = priorityWeights[analysis.priority] || [25, 25, 25, 25];
    
    try {
        window.pieChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: weights,
                    backgroundColor: [
                        'rgba(220, 38, 38, 0.85)',
                        'rgba(234, 88, 12, 0.85)',
                        'rgba(234, 179, 8, 0.85)',
                        'rgba(34, 197, 94, 0.85)'
                    ],
                    borderColor: [
                        'rgb(220, 38, 38)',
                        'rgb(234, 88, 12)',
                        'rgb(234, 179, 8)',
                        'rgb(34, 197, 94)'
                    ],
                    borderWidth: 3,
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor,
                            padding: 16,
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` ${ctx.label}: ${ctx.parsed}%`
                        }
                    }
                }
            }
        });
        console.log('Pie chart created successfully');
    } catch (error) {
        console.error('Error creating pie chart:', error);
    }
    
    console.log('All charts generated successfully');
}

// Copy Reply
document.getElementById('copy-reply-btn').addEventListener('click', () => {
    const reply = document.getElementById('result-reply').textContent;
    navigator.clipboard.writeText(reply).then(() => {
        const btn = document.getElementById('copy-reply-btn');
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => btn.textContent = originalText, 2000);
    });
});

// Copy Suggestion
document.getElementById('copy-suggestion-btn').addEventListener('click', () => {
    const suggestion = document.getElementById('result-email-suggestion').textContent;
    navigator.clipboard.writeText(suggestion).then(() => {
        const btn = document.getElementById('copy-suggestion-btn');
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => btn.textContent = originalText, 2000);
    });
});

// Download PDF
document.getElementById('download-pdf-btn').addEventListener('click', async () => {
    if (!currentAnalysis || !currentEmailText) {
        alert('No analysis available to download');
        return;
    }
    
    // Directly download light mode PDF
    downloadPDFWithTheme('light');
});

async function downloadPDFWithTheme(theme) {
    const btn = document.getElementById('download-pdf-btn');
    btn.classList.add('loading');
    
    try {
        const response = await fetch(`${API_URL}/generate-pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                analysis: currentAnalysis,
                email_text: currentEmailText,
                user_email: currentUser ? currentUser.email : null,
                theme: theme
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `email_analysis_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const errorText = await response.text();
            console.error('PDF generation failed:', errorText);
            alert('Failed to generate PDF. Please try again.');
        }
    } catch (error) {
        console.error('PDF download error:', error);
        alert('Network error. Please check your connection and try again.');
    } finally {
        btn.classList.remove('loading');
    }
}

// Chatbot
document.getElementById('send-chat-btn').addEventListener('click', sendChatMessage);
document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
});

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    if (message.length > 5000) {
        alert('Message is too long. Please keep it under 5000 characters.');
        return;
    }
    
    const btn = document.getElementById('send-chat-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    // Add user message
    addChatMessage(message, 'user');
    input.value = '';
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                user_id: currentUser.id
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.response) {
            addChatMessage(data.response, 'bot');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Chat error:', error);
        addChatMessage('Sorry, I could not process your message. Please try again.', 'bot');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

function addChatMessage(text, type) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    const avatar = type === 'bot' ? '🤖' : '👤';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">${formatMessage(text)}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatMessage(text) {
    // Convert markdown-style formatting
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

// History
async function loadHistory() {
    const container = document.getElementById('history-container');
    
    // Use cache if available and fresh
    const now = Date.now();
    if (historyCache && (now - historyCacheTime) < CACHE_DURATION) {
        displayHistory(historyCache, container);
        return;
    }
    
    container.innerHTML = '<div class="loading-spinner">Loading...</div>';
    
    try {
        const response = await fetch(`${API_URL}/history`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUser.id })
        });
        
        const data = await response.json();
        
        // Cache the result
        historyCache = data;
        historyCacheTime = now;
        
        displayHistory(data, container);
    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Error Loading History</h3>
                <p>Please try again later</p>
            </div>
        `;
    }
}

function displayHistory(data, container) {
    if (data.success && data.history.length > 0) {
        container.innerHTML = '';
        data.history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            // Format date properly
            const date = new Date(item.created_at);
            const formattedDate = date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            });
            
            historyItem.innerHTML = `
                <div class="history-header">
                    <div>
                        <strong>${item.analysis.intent || 'Email Analysis'}</strong>
                        <span style="margin: 0 8px; color: #d1d5db;">•</span>
                        <span style="color: #6b7280;">${item.analysis.tone || 'N/A'}</span>
                    </div>
                    <div class="history-date">${formattedDate}</div>
                </div>
                <div class="history-preview">${item.email_text}</div>
            `;
            
            historyItem.addEventListener('click', () => {
                // Set the email text and analysis
                document.getElementById('email-input').value = item.email_text;
                currentAnalysis = item.analysis;
                currentEmailText = item.email_text;
                
                // Switch to analyzer view
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                document.querySelector('[data-view="analyzer"]').classList.add('active');
                document.getElementById('analyzer-view').classList.add('active');
                
                // Display the full results with charts
                displayResults(item.analysis);
                
                // Scroll to results section smoothly
                setTimeout(() => {
                    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            });
            
            container.appendChild(historyItem);
        });
    } else {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h3>No History Yet</h3>
                <p>Your email analyses will appear here</p>
            </div>
        `;
    }
}

// ===== EMAIL TEMPLATES FUNCTIONALITY =====

let currentTemplateCategory = 'Apology';
let selectedTemplate = null;

// Load templates when Templates view is opened
document.querySelector('[data-view="templates"]').addEventListener('click', () => {
    loadTemplates(currentTemplateCategory);
});

// Category tab switching
document.querySelectorAll('.template-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const category = tab.dataset.category;
        currentTemplateCategory = category;
        
        // Update active tab
        document.querySelectorAll('.template-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Load templates for selected category
        loadTemplates(category);
    });
});

// Load templates function
function loadTemplates(category) {
    const templatesList = document.getElementById('templates-list');
    templatesList.innerHTML = '';
    
    let templates = [];
    
    if (category === 'Custom') {
        // Load custom templates
        templates = getCustomTemplates();
        
        if (templates.length === 0) {
            templatesList.innerHTML = `
                <div class="empty-templates">
                    <div class="empty-templates-icon">📝</div>
                    <h3>No Custom Templates Yet</h3>
                    <p>Create your first custom template using the button below</p>
                </div>
            `;
            return;
        }
    } else {
        // Load built-in templates
        templates = EMAIL_TEMPLATES[category] || [];
    }
    
    templates.forEach(template => {
        const card = document.createElement('div');
        card.className = template.isCustom ? 'template-card custom' : 'template-card';
        
        const preview = template.body.substring(0, 150) + '...';
        
        card.innerHTML = `
            ${template.isCustom ? '<button class="template-delete-btn" data-id="' + template.id + '">×</button>' : ''}
            <h3>${template.name}</h3>
            <p>${preview}</p>
        `;
        
        card.addEventListener('click', (e) => {
            if (!e.target.classList.contains('template-delete-btn')) {
                showTemplatePreview(template);
            }
        });
        
        // Delete button for custom templates
        if (template.isCustom) {
            const deleteBtn = card.querySelector('.template-delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm('Are you sure you want to delete this template?')) {
                    deleteCustomTemplate(template.id);
                    loadTemplates('Custom');
                }
            });
        }
        
        templatesList.appendChild(card);
    });
}

// Show template preview modal
function showTemplatePreview(template) {
    selectedTemplate = template;
    
    document.getElementById('modal-template-name').textContent = template.name;
    document.getElementById('modal-subject').value = template.subject;
    document.getElementById('modal-body').value = template.body;
    
    document.getElementById('template-modal').style.display = 'flex';
}

// Close preview modal
document.getElementById('modal-close').addEventListener('click', () => {
    document.getElementById('template-modal').style.display = 'none';
    selectedTemplate = null;
});

// Use template button
document.getElementById('use-template-btn').addEventListener('click', () => {
    if (selectedTemplate) {
        // Fill the email input with template
        document.getElementById('email-input').value = selectedTemplate.body;
        
        // Switch to analyzer view
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.querySelector('[data-view="analyzer"]').classList.add('active');
        document.getElementById('analyzer-view').classList.add('active');
        
        // Close modal
        document.getElementById('template-modal').style.display = 'none';
        
        // Scroll to input and focus
        setTimeout(() => {
            document.getElementById('email-input').scrollIntoView({ behavior: 'smooth', block: 'start' });
            document.getElementById('email-input').focus();
        }, 100);
    }
});

// Edit & Customize button
document.getElementById('edit-template-btn').addEventListener('click', () => {
    if (selectedTemplate) {
        // Make fields editable
        document.getElementById('modal-subject').removeAttribute('readonly');
        document.getElementById('modal-body').removeAttribute('readonly');
        
        // Change button text
        document.getElementById('edit-template-btn').textContent = 'Save as Custom Template';
        document.getElementById('edit-template-btn').onclick = () => {
            const customTemplate = {
                name: selectedTemplate.name + ' (Customized)',
                category: currentTemplateCategory === 'Custom' ? 'Request' : currentTemplateCategory,
                subject: document.getElementById('modal-subject').value,
                body: document.getElementById('modal-body').value
            };
            
            if (saveCustomTemplate(customTemplate)) {
                alert('Custom template saved successfully!');
                document.getElementById('template-modal').style.display = 'none';
                
                // Switch to Custom tab
                currentTemplateCategory = 'Custom';
                document.querySelectorAll('.template-tab').forEach(t => t.classList.remove('active'));
                document.querySelector('[data-category="Custom"]').classList.add('active');
                loadTemplates('Custom');
            } else {
                alert('Failed to save template. Please try again.');
            }
        };
    }
});

// Create custom template button
document.getElementById('create-template-btn').addEventListener('click', () => {
    document.getElementById('create-template-modal').style.display = 'flex';
    
    // Clear form
    document.getElementById('custom-template-name').value = '';
    document.getElementById('custom-template-category').value = 'Request';
    document.getElementById('custom-template-subject').value = '';
    document.getElementById('custom-template-body').value = '';
});

// Close create modal
document.getElementById('create-modal-close').addEventListener('click', () => {
    document.getElementById('create-template-modal').style.display = 'none';
});

document.getElementById('cancel-create-btn').addEventListener('click', () => {
    document.getElementById('create-template-modal').style.display = 'none';
});

// Save custom template
document.getElementById('save-template-btn').addEventListener('click', () => {
    const name = document.getElementById('custom-template-name').value.trim();
    const category = document.getElementById('custom-template-category').value;
    const subject = document.getElementById('custom-template-subject').value.trim();
    const body = document.getElementById('custom-template-body').value.trim();
    
    if (!name) {
        alert('Please enter a template name');
        return;
    }
    
    if (!subject) {
        alert('Please enter a subject line');
        return;
    }
    
    if (!body) {
        alert('Please enter the email body');
        return;
    }
    
    const customTemplate = {
        name: name,
        category: category,
        subject: subject,
        body: body
    };
    
    if (saveCustomTemplate(customTemplate)) {
        alert('Template created successfully!');
        document.getElementById('create-template-modal').style.display = 'none';
        
        // Switch to Custom tab
        currentTemplateCategory = 'Custom';
        document.querySelectorAll('.template-tab').forEach(t => t.classList.remove('active'));
        document.querySelector('[data-category="Custom"]').classList.add('active');
        loadTemplates('Custom');
    } else {
        alert('Failed to create template. Please try again.');
    }
});

// Close modals when clicking outside
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('template-modal')) {
        e.target.style.display = 'none';
    }
});

// ===== BULK EMAIL ANALYSIS FUNCTIONALITY =====

let bulkEmails = [];
let bulkResults = [];

// Add email button
document.getElementById('add-email-btn').addEventListener('click', () => {
    document.getElementById('add-email-modal').style.display = 'flex';
    document.getElementById('email-label-input').value = '';
    document.getElementById('email-content-input').value = '';
});

// Close add email modal
document.getElementById('add-email-close').addEventListener('click', () => {
    document.getElementById('add-email-modal').style.display = 'none';
});

document.getElementById('cancel-add-email-btn').addEventListener('click', () => {
    document.getElementById('add-email-modal').style.display = 'none';
});

// Save email
document.getElementById('save-email-btn').addEventListener('click', () => {
    const label = document.getElementById('email-label-input').value.trim();
    const content = document.getElementById('email-content-input').value.trim();
    
    if (!content) {
        showToast('Please enter email content', 'warning');
        return;
    }
    
    if (content.length < 10) {
        showToast('Email content is too short (minimum 10 characters)', 'warning');
        return;
    }
    
    const email = {
        id: Date.now(),
        label: label || `Email ${bulkEmails.length + 1}`,
        content: content
    };
    
    bulkEmails.push(email);
    updateBulkEmailsList();
    document.getElementById('add-email-modal').style.display = 'none';
    showToast('Email added successfully!', 'success');
});

// Upload file button
document.getElementById('upload-file-btn').addEventListener('click', () => {
    document.getElementById('bulk-file-input').click();
});

// Handle file upload
document.getElementById('bulk-file-input').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
        const content = event.target.result;
        const emails = content.split('---').map(e => e.trim()).filter(e => e.length > 10);
        
        if (emails.length === 0) {
            showToast('No valid emails found in file. Please separate emails with "---"', 'warning');
            return;
        }
        
        // Get current count for proper numbering
        const startIndex = bulkEmails.length;
        
        emails.forEach((emailContent, index) => {
            bulkEmails.push({
                id: Date.now() + (index * 100), // Add spacing to avoid conflicts
                label: `Email ${startIndex + index + 1}`,
                content: emailContent
            });
        });
        
        updateBulkEmailsList();
        showToast(`Successfully loaded ${emails.length} email(s)`, 'success');
    };
    
    reader.readAsText(file);
    e.target.value = ''; // Reset input
});

// Update emails list
function updateBulkEmailsList() {
    const section = document.getElementById('bulk-emails-section');
    const list = document.getElementById('bulk-emails-list');
    const count = document.getElementById('email-count');
    
    if (bulkEmails.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    count.textContent = bulkEmails.length;
    list.innerHTML = '';
    
    bulkEmails.forEach(email => {
        const item = document.createElement('div');
        item.className = 'bulk-email-item';
        item.innerHTML = `
            <div class="bulk-email-info">
                <div class="bulk-email-label">${email.label}</div>
                <div class="bulk-email-preview">${email.content.substring(0, 100)}...</div>
            </div>
            <div class="bulk-email-actions">
                <button class="view-email-btn" data-id="${email.id}">View</button>
                <button class="remove-email-btn" data-id="${email.id}">Remove</button>
            </div>
        `;
        
        // View button - show modal instead of alert
        item.querySelector('.view-email-btn').addEventListener('click', () => {
            showEmailViewModal(email);
        });
        
        // Remove button
        item.querySelector('.remove-email-btn').addEventListener('click', () => {
            bulkEmails = bulkEmails.filter(e => e.id !== email.id);
            updateBulkEmailsList();
        });
        
        list.appendChild(item);
    });
}

// Show email view modal
function showEmailViewModal(email) {
    document.getElementById('view-email-title').textContent = 'Email Content';
    document.getElementById('view-email-label').textContent = email.label;
    document.getElementById('view-email-content').textContent = email.content;
    document.getElementById('view-email-modal').style.display = 'flex';
}

// Close view email modal
document.getElementById('view-email-close').addEventListener('click', () => {
    document.getElementById('view-email-modal').style.display = 'none';
});

document.getElementById('close-view-email-btn').addEventListener('click', () => {
    document.getElementById('view-email-modal').style.display = 'none';
});

// Copy email content from modal
document.getElementById('copy-email-content-btn').addEventListener('click', () => {
    const content = document.getElementById('view-email-content').textContent;
    navigator.clipboard.writeText(content).then(() => {
        const btn = document.getElementById('copy-email-content-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✓ Copied!';
        setTimeout(() => btn.innerHTML = originalText, 2000);
    });
});

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        padding: 16px 24px;
        margin-bottom: 12px;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        font-size: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        animation: slideIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        min-width: 320px;
        max-width: 500px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        cursor: pointer;
        transition: transform 0.2s ease;
    `;
    
    const colors = {
        'success': 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
        'error': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        'warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        'info': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
    };
    
    const icons = {
        'success': '✓',
        'error': '✗',
        'warning': '⚠',
        'info': '💬'
    };
    
    toast.style.background = colors[type] || colors['info'];
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 20px; flex-shrink: 0;">${icons[type]}</span>
            <span style="flex: 1; line-height: 1.4;">${message}</span>
            <span style="font-size: 18px; opacity: 0.7; flex-shrink: 0;">×</span>
        </div>
    `;
    
    // Add hover effect
    toast.addEventListener('mouseenter', () => {
        toast.style.transform = 'translateY(-2px) scale(1.02)';
    });
    
    toast.addEventListener('mouseleave', () => {
        toast.style.transform = 'translateY(0) scale(1)';
    });
    
    // Click to dismiss
    toast.addEventListener('click', () => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    });
    
    document.getElementById('toast-container').appendChild(toast);
    
    // Auto-dismiss based on message length and type
    const dismissTime = type === 'error' ? 6000 : type === 'warning' ? 5000 : 4000;
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }
    }, dismissTime);
}

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Confirmation modal functionality
let confirmationCallback = null;

function showConfirmation(title, message, onConfirm) {
    document.getElementById('confirmation-title').textContent = title;
    document.getElementById('confirmation-message').textContent = message;
    confirmationCallback = onConfirm;
    document.getElementById('confirmation-modal').style.display = 'flex';
}

function hideConfirmation() {
    document.getElementById('confirmation-modal').style.display = 'none';
    confirmationCallback = null;
}

document.getElementById('confirmation-close').addEventListener('click', hideConfirmation);
document.getElementById('confirmation-cancel-btn').addEventListener('click', hideConfirmation);
document.getElementById('confirmation-confirm-btn').addEventListener('click', () => {
    if (confirmationCallback) {
        confirmationCallback();
    }
    hideConfirmation();
});

// Clear all button
document.getElementById('clear-all-btn').addEventListener('click', () => {
    showConfirmation(
        'Clear All Emails',
        'Are you sure you want to clear all emails? This action cannot be undone.',
        () => {
            bulkEmails = [];
            bulkResults = [];
            updateBulkEmailsList();
            document.getElementById('bulk-results-section').style.display = 'none';
        }
    );
});

// Analyze all button
document.getElementById('analyze-all-btn').addEventListener('click', async () => {
    if (bulkEmails.length === 0) {
        showToast('Please add emails first', 'warning');
        return;
    }
    
    const btn = document.getElementById('analyze-all-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    bulkResults = [];
    
    // Show progress
    const progressDiv = document.createElement('div');
    progressDiv.className = 'progress-indicator';
    progressDiv.innerHTML = `
        <div class="progress-bar">
            <div class="progress-fill" id="bulk-progress-fill" style="width: 0%"></div>
        </div>
        <div class="progress-text" id="bulk-progress-text">Analyzing 0 of ${bulkEmails.length} emails...</div>
    `;
    document.getElementById('bulk-emails-section').appendChild(progressDiv);
    
    // Analyze each email
    for (let i = 0; i < bulkEmails.length; i++) {
        const email = bulkEmails[i];
        
        try {
            // Validate email content
            if (!email.content || email.content.trim().length < 10) {
                bulkResults.push({
                    email: email,
                    analysis: null,
                    error: 'Email content too short (minimum 10 characters)'
                });
                continue;
            }
            
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_text: email.content.trim(),
                    user_id: currentUser.id
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`Analysis failed for ${email.label}:`, errorText);
                bulkResults.push({
                    email: email,
                    analysis: null,
                    error: `Server error: ${response.status}`
                });
                continue;
            }
            
            const data = await response.json();
            
            if (data.success && data.analysis) {
                bulkResults.push({
                    email: email,
                    analysis: data.analysis
                });
            } else {
                bulkResults.push({
                    email: email,
                    analysis: null,
                    error: data.detail || 'Analysis failed'
                });
            }
        } catch (error) {
            console.error(`Error analyzing ${email.label}:`, error);
            bulkResults.push({
                email: email,
                analysis: null,
                error: error.message || 'Network error'
            });
        }
        
        // Update progress
        const progress = ((i + 1) / bulkEmails.length) * 100;
        document.getElementById('bulk-progress-fill').style.width = `${progress}%`;
        document.getElementById('bulk-progress-text').textContent = `Analyzing ${i + 1} of ${bulkEmails.length} emails...`;
    }
    
    // Remove progress indicator
    progressDiv.remove();
    
    // Display results
    displayBulkResults();
    
    btn.classList.remove('loading');
    btn.disabled = false;
});

// Display bulk results
function displayBulkResults() {
    const section = document.getElementById('bulk-results-section');
    const table = document.getElementById('bulk-results-table');
    
    if (bulkResults.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    
    // Generate detailed table with all scores
    let tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Tone</th>
                    <th>Intent</th>
                    <th>Sentiment</th>
                    <th>Priority</th>
                    <th>Professionalism</th>
                    <th>Overall Score</th>
                    <th>Readability</th>
                    <th>Clarity</th>
                    <th>Engagement</th>
                    <th>Grammar Issues</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    bulkResults.forEach((result, index) => {
        if (result.analysis) {
            const a = result.analysis;
            const scores = a.email_scores || {};
            tableHTML += `
                <tr>
                    <td><strong>${result.email.label}</strong></td>
                    <td>${a.tone || 'N/A'}</td>
                    <td>${a.intent || 'N/A'} (${a.confidence || 'N/A'})</td>
                    <td><span class="result-badge ${(a.sentiment || '').toLowerCase()}">${a.sentiment || 'N/A'}</span></td>
                    <td><span class="result-badge ${(a.priority || '').toLowerCase()}">${a.priority || 'N/A'}</span></td>
                    <td><strong style="color: ${getProfessionalismColor(a.professionalism_score)};">${a.professionalism_score || 'N/A'}/10</strong></td>
                    <td><strong style="color: ${getScoreColor(scores.overall_score)};">${scores.overall_score || 'N/A'}/100</strong></td>
                    <td>${scores.readability_score || 'N/A'}/100</td>
                    <td>${scores.clarity_score || 'N/A'}/100</td>
                    <td>${scores.engagement_score || 'N/A'}/100</td>
                    <td>${a.grammar_issues ? a.grammar_issues.length : 0}</td>
                    <td><span class="result-badge positive">✓ Success</span></td>
                </tr>
            `;
        } else {
            tableHTML += `
                <tr>
                    <td><strong>${result.email.label}</strong></td>
                    <td colspan="11"><span class="result-badge negative">✗ ${result.error || 'Failed'}</span></td>
                </tr>
            `;
        }
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    table.innerHTML = tableHTML;
    
    // Generate professionalism chart
    generateProfessionalismChart();
    
    // Scroll to results
    section.scrollIntoView({ behavior: 'smooth' });
}

// Helper function to get color based on professionalism score
function getProfessionalismColor(score) {
    if (!score) return '#6b7280';
    const s = parseInt(score);
    if (s >= 8) return '#22c55e';
    if (s >= 6) return '#eab308';
    if (s >= 4) return '#ea580c';
    return '#dc2626';
}

// Helper function to get color based on overall score
function getScoreColor(score) {
    if (!score) return '#6b7280';
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#667eea';
    if (score >= 40) return '#eab308';
    return '#ef4444';
}

// Generate professionalism chart
function generateProfessionalismChart() {
    const canvas = document.getElementById('bulkProfessionalismChart');
    if (!canvas) return;
    
    // Destroy existing chart
    if (window.bulkProfChart) {
        window.bulkProfChart.destroy();
    }
    
    // Get successful results only
    const successfulResults = bulkResults.filter(r => r.analysis);
    
    if (successfulResults.length === 0) {
        document.getElementById('bulk-chart-section').style.display = 'none';
        return;
    }
    
    document.getElementById('bulk-chart-section').style.display = 'block';
    
    // Split into groups of 10
    const groups = [];
    for (let i = 0; i < successfulResults.length; i += 10) {
        groups.push(successfulResults.slice(i, i + 10));
    }
    
    // Current page for chart
    let currentChartPage = 0;
    
    function renderChart(pageIndex) {
        const chartData = groups[pageIndex];
        const labels = chartData.map(r => r.email.label);
        const professionalismScores = chartData.map(r => (r.analysis.professionalism_score || 0) * 10); // Convert to 0-100 scale
        const overallScores = chartData.map(r => r.analysis.email_scores?.overall_score || 0);
        const clarityScores = chartData.map(r => r.analysis.email_scores?.clarity_score || 0);
        const engagementScores = chartData.map(r => r.analysis.email_scores?.engagement_score || 0);
        
        // Get theme colors
        const isDark = document.body.getAttribute('data-theme') !== 'light';
        const textColor = isDark ? '#ffffff' : '#1f2937';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        // Destroy previous chart
        if (window.bulkProfChart) {
            window.bulkProfChart.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        window.bulkProfChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Professionalism Score',
                        data: professionalismScores,
                        backgroundColor: 'rgba(99, 102, 241, 0.8)',
                        borderColor: 'rgb(99, 102, 241)',
                        borderWidth: 2,
                        borderRadius: 6
                    },
                    {
                        label: 'Overall Quality',
                        data: overallScores,
                        backgroundColor: 'rgba(34, 197, 94, 0.8)',
                        borderColor: 'rgb(34, 197, 94)',
                        borderWidth: 2,
                        borderRadius: 6
                    },
                    {
                        label: 'Clarity',
                        data: clarityScores,
                        backgroundColor: 'rgba(168, 85, 247, 0.8)',
                        borderColor: 'rgb(168, 85, 247)',
                        borderWidth: 2,
                        borderRadius: 6
                    },
                    {
                        label: 'Engagement',
                        data: engagementScores,
                        backgroundColor: 'rgba(236, 72, 153, 0.8)',
                        borderColor: 'rgb(236, 72, 153)',
                        borderWidth: 2,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { 
                            color: textColor,
                            font: { size: 12 },
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: { color: gridColor },
                        title: {
                            display: true,
                            text: 'Score (%)',
                            color: textColor,
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    x: {
                        ticks: { 
                            color: textColor,
                            font: { size: 11, weight: 'bold' },
                            maxRotation: 45,
                            minRotation: 45
                        },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { 
                            color: textColor,
                            font: { size: 13, weight: 'bold' },
                            padding: 15
                        }
                    },
                    title: {
                        display: true,
                        text: groups.length > 1 
                            ? `Emails ${pageIndex * 10 + 1}-${Math.min((pageIndex + 1) * 10, successfulResults.length)} of ${successfulResults.length}`
                            : `All ${successfulResults.length} Email${successfulResults.length > 1 ? 's' : ''}`,
                        color: textColor,
                        font: { size: 14, weight: 'bold' },
                        padding: { bottom: 15 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Render first page
    renderChart(currentChartPage);
    
    // Add pagination controls if more than 10 emails
    if (groups.length > 1) {
        const chartSection = document.getElementById('bulk-chart-section');
        
        // Remove existing pagination if any
        const existingPagination = chartSection.querySelector('.chart-pagination');
        if (existingPagination) {
            existingPagination.remove();
        }
        
        const paginationDiv = document.createElement('div');
        paginationDiv.className = 'chart-pagination';
        paginationDiv.style.cssText = 'display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 20px;';
        
        const prevBtn = document.createElement('button');
        prevBtn.className = 'btn btn-secondary btn-sm';
        prevBtn.innerHTML = '← Previous 10';
        prevBtn.style.cssText = 'padding: 8px 16px;';
        prevBtn.disabled = currentChartPage === 0;
        prevBtn.onclick = () => {
            if (currentChartPage > 0) {
                currentChartPage--;
                renderChart(currentChartPage);
                updatePaginationButtons();
            }
        };
        
        const pageInfo = document.createElement('span');
        pageInfo.className = 'page-info';
        pageInfo.style.cssText = 'font-weight: bold; color: var(--text-primary); padding: 0 15px;';
        pageInfo.textContent = `Page ${currentChartPage + 1} of ${groups.length}`;
        
        const nextBtn = document.createElement('button');
        nextBtn.className = 'btn btn-secondary btn-sm';
        nextBtn.innerHTML = 'Next 10 →';
        nextBtn.style.cssText = 'padding: 8px 16px;';
        nextBtn.disabled = currentChartPage === groups.length - 1;
        nextBtn.onclick = () => {
            if (currentChartPage < groups.length - 1) {
                currentChartPage++;
                renderChart(currentChartPage);
                updatePaginationButtons();
            }
        };
        
        function updatePaginationButtons() {
            prevBtn.disabled = currentChartPage === 0;
            nextBtn.disabled = currentChartPage === groups.length - 1;
            pageInfo.textContent = `Page ${currentChartPage + 1} of ${groups.length}`;
        }
        
        paginationDiv.appendChild(prevBtn);
        paginationDiv.appendChild(pageInfo);
        paginationDiv.appendChild(nextBtn);
        chartSection.appendChild(paginationDiv);
        
        // Show info toast
        showToast(`📊 Chart shows 10 emails per page. Total: ${successfulResults.length} emails analyzed`, 'info');
    }
}

// Export CSV
document.getElementById('export-csv-btn').addEventListener('click', () => {
    if (bulkResults.length === 0) {
        showToast('No results to export', 'warning');
        return;
    }
    
    let csv = 'Email Label,Tone,Intent,Sentiment,Priority,Professionalism Score,Overall Score,Readability,Clarity,Engagement,Grammar Issues,Key Problems\n';
    
    bulkResults.forEach(result => {
        if (result.analysis) {
            const a = result.analysis;
            const scores = a.email_scores || {};
            csv += `"${result.email.label}",`;
            csv += `"${a.tone || ''}",`;
            csv += `"${a.intent || ''}",`;
            csv += `"${a.sentiment || ''}",`;
            csv += `"${a.priority || ''}",`;
            csv += `"${a.professionalism_score || ''} out of 10",`;
            csv += `"${scores.overall_score || ''}",`;
            csv += `"${scores.readability_score || ''}",`;
            csv += `"${scores.clarity_score || ''}",`;
            csv += `"${scores.engagement_score || ''}",`;
            csv += `"${a.grammar_issues ? a.grammar_issues.length : 0}",`;
            csv += `"${a.key_problems ? a.key_problems.join('; ') : ''}"\n`;
        }
    });
    
    downloadFile(csv, 'bulk-analysis-results.csv', 'text/csv');
    showToast('CSV exported successfully!', 'success');
});

// Export Excel (HTML table format)
document.getElementById('export-excel-btn').addEventListener('click', () => {
    if (bulkResults.length === 0) {
        showToast('No results to export', 'warning');
        return;
    }
    
    let html = '<html><head><meta charset="utf-8"><title>Bulk Analysis Results</title>';
    html += '<style>table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid black; padding: 8px; text-align: left; } th { background-color: #667eea; color: white; font-weight: bold; }</style>';
    html += '</head><body>';
    html += '<h1>Email Analysis Results</h1>';
    html += '<table>';
    html += '<tr><th>Email</th><th>Tone</th><th>Intent</th><th>Sentiment</th><th>Priority</th><th>Professionalism Score</th><th>Overall Score</th><th>Readability</th><th>Clarity</th><th>Engagement</th><th>Grammar Issues</th><th>Key Problems</th></tr>';
    
    bulkResults.forEach(result => {
        if (result.analysis) {
            const a = result.analysis;
            const scores = a.email_scores || {};
            // Use style="mso-number-format:'\@';" to force text format in Excel
            html += '<tr>';
            html += `<td>${result.email.label}</td>`;
            html += `<td>${a.tone || ''}</td>`;
            html += `<td>${a.intent || ''}</td>`;
            html += `<td>${a.sentiment || ''}</td>`;
            html += `<td>${a.priority || ''}</td>`;
            html += `<td style="mso-number-format:'0\\.0';">${a.professionalism_score || ''} out of 10</td>`;
            html += `<td style="mso-number-format:'0';">${scores.overall_score || ''}</td>`;
            html += `<td style="mso-number-format:'0';">${scores.readability_score || ''}</td>`;
            html += `<td style="mso-number-format:'0';">${scores.clarity_score || ''}</td>`;
            html += `<td style="mso-number-format:'0';">${scores.engagement_score || ''}</td>`;
            html += `<td>${a.grammar_issues ? a.grammar_issues.length : 0}</td>`;
            html += `<td>${a.key_problems ? a.key_problems.join('; ') : ''}</td>`;
            html += '</tr>';
        }
    });
    
    html += '</table></body></html>';
    
    downloadFile(html, 'bulk-analysis-results.xls', 'application/vnd.ms-excel');
});

// Compare side-by-side
document.getElementById('compare-btn').addEventListener('click', () => {
    if (bulkResults.length === 0) {
        showToast('No results to compare', 'warning');
        return;
    }
    
    const modal = document.getElementById('comparison-modal');
    const body = document.getElementById('comparison-body');
    
    let html = '<div class="comparison-grid">';
    
    bulkResults.forEach(result => {
        if (result.analysis) {
            const a = result.analysis;
            html += `
                <div class="comparison-card">
                    <h3>${result.email.label}</h3>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Summary</div>
                        <div class="comparison-field-value">${a.summary || 'N/A'}</div>
                    </div>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Tone</div>
                        <div class="comparison-field-value">${a.tone || 'N/A'}</div>
                    </div>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Intent</div>
                        <div class="comparison-field-value">${a.intent || 'N/A'} (${a.confidence || 'N/A'})</div>
                    </div>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Sentiment</div>
                        <div class="comparison-field-value">${a.sentiment || 'N/A'} (${a.polarity || 'N/A'})</div>
                    </div>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Priority</div>
                        <div class="comparison-field-value">${a.priority || 'N/A'}</div>
                    </div>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Professionalism Score</div>
                        <div class="comparison-field-value">${a.professionalism_score || 'N/A'}/10</div>
                    </div>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Grammar Issues</div>
                        <div class="comparison-field-value">${a.grammar_issues ? a.grammar_issues.length : 0} issue(s)</div>
                    </div>
                    <div class="comparison-field">
                        <div class="comparison-field-label">Key Problems</div>
                        <div class="comparison-field-value">${a.key_problems ? a.key_problems.join(', ') : 'None'}</div>
                    </div>
                </div>
            `;
        }
    });
    
    html += '</div>';
    body.innerHTML = html;
    modal.style.display = 'flex';
});

// Close comparison modal
document.getElementById('comparison-close').addEventListener('click', () => {
    document.getElementById('comparison-modal').style.display = 'none';
});

// Download file helper
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ===== TONE ADJUSTER FUNCTIONALITY =====

let currentAdjustedText = '';

// Formality slider update
document.getElementById('formality-slider').addEventListener('input', (e) => {
    document.getElementById('formality-value').textContent = e.target.value;
});

// Quick conversion buttons
document.querySelectorAll('.tone-convert-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const text = document.getElementById('tone-input').value.trim();
        
        if (!text) {
            alert('Please enter text to adjust');
            return;
        }
        
        if (text.length < 5) {
            alert('Text is too short. Please enter at least 5 characters.');
            return;
        }
        
        const conversionType = btn.dataset.type;
        
        btn.classList.add('loading');
        btn.disabled = true;
        
        try {
            const response = await fetch(`${API_URL}/adjust-tone`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    conversion_type: conversionType
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Server error:', errorData);
                alert(`Error: ${errorData.detail || 'Failed to adjust tone'}`);
                return;
            }
            
            const data = await response.json();
            
            if (data.success && data.adjusted_text) {
                currentAdjustedText = data.adjusted_text;
                displayAdjustedText(data.adjusted_text, conversionType);
            } else {
                alert('Tone adjustment failed. Please try again.');
            }
        } catch (error) {
            console.error('Tone adjustment error:', error);
            alert('Failed to adjust tone. Please check your connection and try again.');
        } finally {
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    });
});

// Apply formality level
document.getElementById('apply-formality-btn').addEventListener('click', async () => {
    const text = document.getElementById('tone-input').value.trim();
    
    if (!text) {
        alert('Please enter text to adjust');
        return;
    }
    
    if (text.length < 5) {
        alert('Text is too short. Please enter at least 5 characters.');
        return;
    }
    
    const formalityLevel = parseInt(document.getElementById('formality-slider').value);
    const btn = document.getElementById('apply-formality-btn');
    
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/adjust-tone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                conversion_type: 'formality_slider',
                formality_level: formalityLevel
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert(`Error: ${errorData.detail || 'Failed to adjust tone'}`);
            return;
        }
        
        const data = await response.json();
        
        if (data.success && data.adjusted_text) {
            currentAdjustedText = data.adjusted_text;
            displayAdjustedText(data.adjusted_text, `Formality Level ${formalityLevel}`);
        } else {
            alert('Tone adjustment failed. Please try again.');
        }
    } catch (error) {
        console.error('Tone adjustment error:', error);
        alert('Failed to adjust tone. Please check your connection and try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Display adjusted text
function displayAdjustedText(text, conversionType) {
    const previewEl = document.getElementById('tone-preview');
    const badgeEl = document.getElementById('preview-badge');
    const actionsEl = document.getElementById('tone-actions');
    
    previewEl.innerHTML = `<div class="adjusted-text">${text.replace(/\n/g, '<br>')}</div>`;
    
    // Set badge text
    const badgeTexts = {
        'casual_to_formal': 'Casual → Formal',
        'aggressive_to_diplomatic': 'Aggressive → Diplomatic'
    };
    badgeEl.textContent = badgeTexts[conversionType] || conversionType;
    badgeEl.style.display = 'inline-block';
    
    actionsEl.style.display = 'flex';
}

// Copy adjusted text
document.getElementById('copy-adjusted-btn').addEventListener('click', () => {
    if (!currentAdjustedText) {
        alert('No adjusted text to copy');
        return;
    }
    
    navigator.clipboard.writeText(currentAdjustedText).then(() => {
        const btn = document.getElementById('copy-adjusted-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✓ Copied!';
        setTimeout(() => btn.innerHTML = originalText, 2000);
    });
});

// Use adjusted text in analyzer
document.getElementById('use-adjusted-btn').addEventListener('click', () => {
    if (!currentAdjustedText) {
        alert('No adjusted text to use');
        return;
    }
    
    // Set the adjusted text in the analyzer
    document.getElementById('email-input').value = currentAdjustedText;
    
    // Switch to analyzer view
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelector('[data-view="analyzer"]').classList.add('active');
    document.getElementById('analyzer-view').classList.add('active');
    
    // Scroll to input smoothly
    setTimeout(() => {
        document.getElementById('email-input').scrollIntoView({ behavior: 'smooth', block: 'start' });
        document.getElementById('email-input').focus();
    }, 100);
});

// Reset tone adjuster
document.getElementById('reset-tone-btn').addEventListener('click', () => {
    document.getElementById('tone-input').value = '';
    document.getElementById('tone-preview').innerHTML = `
        <div class="preview-placeholder">
            <div class="preview-icon">✨</div>
            <p>Your adjusted text will appear here</p>
            <p class="preview-hint">Use the controls on the left to transform your text</p>
        </div>
    `;
    document.getElementById('preview-badge').style.display = 'none';
    document.getElementById('tone-actions').style.display = 'none';
    document.getElementById('formality-slider').value = 50;
    document.getElementById('formality-value').textContent = '50';
    currentAdjustedText = '';
});

// ===== EMAIL LENGTH OPTIMIZER FUNCTIONALITY =====

let currentOptimizedText = '';

// Tool tabs switching
document.querySelectorAll('.tool-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tool = tab.dataset.tool;
        
        // Update active tab
        document.querySelectorAll('.tool-tab').forEach(t => {
            t.style.background = 'var(--card-bg)';
            t.style.color = 'var(--text-primary)';
            t.classList.remove('active');
        });
        tab.style.background = 'var(--primary-color)';
        tab.style.color = 'white';
        tab.classList.add('active');
        
        // Show corresponding tool
        document.querySelectorAll('.tool-content').forEach(content => {
            content.style.display = 'none';
            content.classList.remove('active');
        });
        document.getElementById(`${tool}-tool`).style.display = 'block';
        document.getElementById(`${tool}-tool`).classList.add('active');
    });
});

// Analyze Length
document.getElementById('analyze-length-btn').addEventListener('click', async () => {
    const text = document.getElementById('length-input').value.trim();
    
    if (!text) {
        alert('Please enter text to analyze');
        return;
    }
    
    const btn = document.getElementById('analyze-length-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/optimize-length`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                action: 'analyze'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.analysis) {
            displayLengthAnalysis(data.analysis);
        } else {
            alert('Analysis failed. Please try again.');
        }
    } catch (error) {
        console.error('Length analysis error:', error);
        alert('Failed to analyze length. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Summarize Email
document.getElementById('summarize-btn').addEventListener('click', async () => {
    const text = document.getElementById('length-input').value.trim();
    
    if (!text) {
        alert('Please enter text to summarize');
        return;
    }
    
    const btn = document.getElementById('summarize-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/optimize-length`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                action: 'summarize'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.optimized_text) {
            currentOptimizedText = data.optimized_text;
            displayOptimizedText(data.optimized_text, 'Summarized');
            if (data.analysis) {
                displayLengthAnalysis(data.analysis);
            }
        } else {
            alert('Summarization failed. Please try again.');
        }
    } catch (error) {
        console.error('Summarization error:', error);
        alert('Failed to summarize. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Expand Email
document.getElementById('expand-btn').addEventListener('click', async () => {
    const text = document.getElementById('length-input').value.trim();
    
    if (!text) {
        alert('Please enter text to expand');
        return;
    }
    
    const btn = document.getElementById('expand-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/optimize-length`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                action: 'expand'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.optimized_text) {
            currentOptimizedText = data.optimized_text;
            displayOptimizedText(data.optimized_text, 'Expanded');
            if (data.analysis) {
                displayLengthAnalysis(data.analysis);
            }
        } else {
            alert('Expansion failed. Please try again.');
        }
    } catch (error) {
        console.error('Expansion error:', error);
        alert('Failed to expand. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Auto-Optimize
document.getElementById('optimize-btn').addEventListener('click', async () => {
    const text = document.getElementById('length-input').value.trim();
    
    if (!text) {
        alert('Please enter text to optimize');
        return;
    }
    
    const btn = document.getElementById('optimize-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/optimize-length`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                action: 'optimize'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.result) {
            const result = data.result;
            if (result.action === 'none') {
                alert(result.message);
                displayOptimizedText(result.optimized_text, 'Already Optimal');
            } else {
                currentOptimizedText = result.optimized_text;
                const actionLabel = result.action === 'summarize' ? 'Summarized' : 'Expanded';
                displayOptimizedText(result.optimized_text, actionLabel);
            }
        } else {
            alert('Optimization failed. Please try again.');
        }
    } catch (error) {
        console.error('Optimization error:', error);
        alert('Failed to optimize. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Display Length Analysis
function displayLengthAnalysis(analysis) {
    const analysisDiv = document.getElementById('length-analysis');
    analysisDiv.style.display = 'block';
    
    document.getElementById('word-count').textContent = analysis.word_count;
    document.getElementById('char-count').textContent = analysis.char_count;
    document.getElementById('sentence-count').textContent = analysis.sentence_count;
    document.getElementById('optimal-range').textContent = analysis.optimal_range;
    
    const statusEl = document.getElementById('length-status');
    statusEl.textContent = analysis.status;
    
    // Color code status
    const colors = {
        'Too Short': '#dc2626',
        'Brief': '#eab308',
        'Optimal': '#22c55e',
        'Lengthy': '#eab308',
        'Too Long': '#dc2626'
    };
    statusEl.style.color = colors[analysis.status] || '#6b7280';
    
    document.getElementById('length-recommendation').textContent = analysis.recommendation;
}

// Display Optimized Text
function displayOptimizedText(text, action) {
    const previewEl = document.getElementById('length-preview');
    const badgeEl = document.getElementById('length-preview-badge');
    const actionsEl = document.getElementById('length-actions');
    
    previewEl.innerHTML = `<div class="adjusted-text" style="white-space: pre-wrap; line-height: 1.6;">${text.replace(/\n/g, '<br>')}</div>`;
    
    badgeEl.textContent = action;
    badgeEl.style.display = 'inline-block';
    badgeEl.style.background = 'var(--primary-color)';
    badgeEl.style.color = 'white';
    badgeEl.style.padding = '4px 12px';
    badgeEl.style.borderRadius = '12px';
    badgeEl.style.fontSize = '12px';
    badgeEl.style.fontWeight = 'bold';
    
    actionsEl.style.display = 'flex';
}

// Copy Optimized Text
document.getElementById('copy-optimized-btn').addEventListener('click', () => {
    if (!currentOptimizedText) {
        alert('No optimized text to copy');
        return;
    }
    
    navigator.clipboard.writeText(currentOptimizedText).then(() => {
        const btn = document.getElementById('copy-optimized-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✓ Copied!';
        setTimeout(() => btn.innerHTML = originalText, 2000);
    });
});

// Use Optimized Text in Analyzer
document.getElementById('use-optimized-btn').addEventListener('click', () => {
    if (!currentOptimizedText) {
        alert('No optimized text to use');
        return;
    }
    
    // Set the optimized text in the analyzer
    document.getElementById('email-input').value = currentOptimizedText;
    
    // Switch to analyzer view
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelector('[data-view="analyzer"]').classList.add('active');
    document.getElementById('analyzer-view').classList.add('active');
    
    // Scroll to input smoothly
    setTimeout(() => {
        document.getElementById('email-input').scrollIntoView({ behavior: 'smooth', block: 'start' });
        document.getElementById('email-input').focus();
    }, 100);
});

// Reset Length Optimizer
document.getElementById('reset-length-btn').addEventListener('click', () => {
    document.getElementById('length-input').value = '';
    document.getElementById('length-preview').innerHTML = `
        <div class="preview-placeholder">
            <div class="preview-icon" style="font-size: 48px; margin-bottom: 15px;">📏</div>
            <p>Your optimized text will appear here</p>
            <p class="preview-hint" style="color: var(--text-secondary); font-size: 14px; margin-top: 10px;">Use the actions on the left to optimize your email length</p>
        </div>
    `;
    document.getElementById('length-preview-badge').style.display = 'none';
    document.getElementById('length-actions').style.display = 'none';
    document.getElementById('length-analysis').style.display = 'none';
    currentOptimizedText = '';
});

// ===== SUBJECT LINE ANALYZER FUNCTIONALITY =====

// Analyze Subject Line
document.getElementById('analyze-subject-btn').addEventListener('click', async () => {
    const subject = document.getElementById('subject-input').value.trim();
    
    if (!subject) {
        alert('Please enter a subject line');
        return;
    }
    
    const btn = document.getElementById('analyze-subject-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/analyze-subject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject: subject,
                action: 'analyze'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.analysis) {
            displaySubjectAnalysis(data.analysis);
        } else {
            alert('Analysis failed. Please try again.');
        }
    } catch (error) {
        console.error('Subject analysis error:', error);
        alert('Failed to analyze subject line. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Get Suggestions
document.getElementById('suggest-subject-btn').addEventListener('click', async () => {
    const subject = document.getElementById('subject-input').value.trim();
    
    if (!subject) {
        alert('Please enter a subject line');
        return;
    }
    
    const btn = document.getElementById('suggest-subject-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/analyze-subject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject: subject,
                action: 'suggest'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.suggestions) {
            displaySubjectSuggestions(data.suggestions);
        } else {
            alert('Failed to generate suggestions. Please try again.');
        }
    } catch (error) {
        console.error('Subject suggestions error:', error);
        alert('Failed to generate suggestions. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Generate A/B Tests
document.getElementById('ab-test-btn').addEventListener('click', async () => {
    const subject = document.getElementById('subject-input').value.trim();
    
    if (!subject) {
        alert('Please enter a subject line');
        return;
    }
    
    const btn = document.getElementById('ab-test-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/analyze-subject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject: subject,
                action: 'ab_test'
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.ab_tests) {
            displayABTests(data.ab_tests);
        } else {
            alert('Failed to generate A/B tests. Please try again.');
        }
    } catch (error) {
        console.error('A/B test generation error:', error);
        alert('Failed to generate A/B tests. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Display Subject Analysis
function displaySubjectAnalysis(analysis) {
    const analysisDiv = document.getElementById('subject-analysis');
    analysisDiv.style.display = 'block';
    
    document.getElementById('subject-score').textContent = analysis.score;
    document.getElementById('subject-grade').textContent = `Grade: ${analysis.grade}`;
    document.getElementById('subject-grade-text').textContent = analysis.grade_text;
    
    document.getElementById('subject-char-count').textContent = analysis.char_count;
    document.getElementById('subject-word-count').textContent = analysis.word_count;
    document.getElementById('subject-sentiment').textContent = analysis.sentiment;
    
    const spamEl = document.getElementById('subject-spam-risk');
    spamEl.textContent = analysis.spam_risk;
    spamEl.style.color = analysis.spam_risk === 'High' ? '#dc2626' : analysis.spam_risk === 'Medium' ? '#eab308' : '#22c55e';
    
    const openRate = analysis.predicted_open_rate;
    document.getElementById('subject-open-rate').textContent = `${openRate.min}% - ${openRate.max}% (avg: ${openRate.average}%)`;
    
    // Display insights
    const insightsList = document.getElementById('subject-insights-list');
    insightsList.innerHTML = '';
    
    analysis.insights.forEach(insight => {
        const insightDiv = document.createElement('div');
        insightDiv.style.cssText = 'padding: 10px; margin-bottom: 8px; border-radius: 6px; border-left: 4px solid;';
        
        const colors = {
            'success': '#22c55e',
            'warning': '#eab308',
            'danger': '#dc2626',
            'info': '#3b82f6'
        };
        
        insightDiv.style.borderColor = colors[insight.type] || '#6b7280';
        insightDiv.style.background = 'var(--input-bg)';
        
        insightDiv.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 4px;">${insight.category}</div>
            <div style="font-size: 14px;">${insight.message}</div>
        `;
        
        insightsList.appendChild(insightDiv);
    });
    
    // Show in results
    document.getElementById('subject-results-badge').textContent = 'Analysis Complete';
    document.getElementById('subject-results-badge').style.display = 'inline-block';
}

// Display Subject Suggestions
function displaySubjectSuggestions(suggestions) {
    const resultsDiv = document.getElementById('subject-results');
    const badge = document.getElementById('subject-results-badge');
    
    badge.textContent = 'Suggestions';
    badge.style.display = 'inline-block';
    
    let html = `
        <h4 style="margin-bottom: 15px;">💡 Improved Subject Lines</h4>
        <div style="padding: 10px; background: var(--input-bg); border-radius: 6px; margin-bottom: 15px;">
            <strong>Original:</strong> ${suggestions.original}<br>
            <strong>Score:</strong> ${suggestions.original_score}/100
        </div>
    `;
    
    suggestions.suggestions.forEach((sug, index) => {
        html += `
            <div style="padding: 15px; background: var(--input-bg); border-radius: 8px; margin-bottom: 10px; border-left: 4px solid var(--primary-color);">
                <div style="font-weight: bold; margin-bottom: 8px;">✨ Suggestion ${index + 1}</div>
                <div style="font-size: 16px; margin-bottom: 8px; color: var(--primary-color);">${sug.subject}</div>
                <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 4px;">🎯 ${sug.reason}</div>
                <div style="font-size: 14px; color: #22c55e;">📈 ${sug.expected_improvement}</div>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

// Display A/B Tests
function displayABTests(abTests) {
    const resultsDiv = document.getElementById('subject-results');
    const badge = document.getElementById('subject-results-badge');
    
    badge.textContent = 'A/B Tests';
    badge.style.display = 'inline-block';
    
    let html = `
        <h4 style="margin-bottom: 15px;">🧪 A/B Test Variations</h4>
        <div style="padding: 15px; background: var(--input-bg); border-radius: 8px; margin-bottom: 15px;">
            <strong>Test Plan:</strong><br>
            <div style="margin-top: 8px; font-size: 14px;">
                • ${abTests.test_plan.recommended_sample_size}<br>
                • ${abTests.test_plan.duration}<br>
                • Metric: ${abTests.test_plan.success_metric}<br>
                • ${abTests.test_plan.statistical_significance}
            </div>
        </div>
    `;
    
    abTests.variations.forEach(variation => {
        html += `
            <div style="padding: 15px; background: var(--input-bg); border-radius: 8px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-weight: bold; font-size: 18px; color: var(--primary-color);">Version ${variation.version}</div>
                    <div style="padding: 4px 12px; background: var(--primary-color); color: white; border-radius: 12px; font-size: 12px;">${variation.strategy}</div>
                </div>
                <div style="font-size: 16px; margin-bottom: 8px;">${variation.subject}</div>
                <div style="font-size: 14px; color: var(--text-secondary);">🎯 ${variation.focus}</div>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}


// ===== MULTI-LANGUAGE SUPPORT FUNCTIONALITY =====

// Detect Language
document.getElementById('detect-language-btn').addEventListener('click', async () => {
    const text = document.getElementById('detect-text').value.trim();
    
    if (!text) {
        alert('Please enter text to detect language');
        return;
    }
    
    const btn = document.getElementById('detect-language-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/detect-language`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        
        if (data.success && data.language) {
            displayLanguageDetection(data.language);
        } else {
            alert('Language detection failed. Please try again.');
        }
    } catch (error) {
        console.error('Language detection error:', error);
        alert('Failed to detect language. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Display Language Detection Result
function displayLanguageDetection(language) {
    const resultDiv = document.getElementById('detected-language-result');
    resultDiv.style.display = 'block';
    
    const supportedBadge = language.supported 
        ? '<span class="language-badge">✓ Supported</span>' 
        : '<span class="language-badge" style="background: #ef4444;">✗ Not Supported</span>';
    
    resultDiv.innerHTML = `
        <h3>🔍 Detection Result</h3>
        <div class="language-result-item">
            <div class="language-result-label">Detected Language:</div>
            <div class="language-result-value">
                ${supportedBadge}
                <strong style="font-size: 18px; color: var(--text-primary);">${language.name}</strong>
                <span style="color: var(--text-secondary);">(${language.code})</span>
            </div>
        </div>
    `;
}

// Translate Email
document.getElementById('translate-btn').addEventListener('click', async () => {
    const text = document.getElementById('translate-source').value.trim();
    const targetLang = document.getElementById('target-language').value;
    
    if (!text) {
        alert('Please enter text to translate');
        return;
    }
    
    if (text.length < 3) {
        alert('Text is too short. Please enter at least 3 characters.');
        return;
    }
    
    const btn = document.getElementById('translate-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    // Show translating message
    const resultDiv = document.getElementById('translation-result');
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `
        <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
            <div style="font-size: 24px; margin-bottom: 10px;">🔄</div>
            <div>Translating to ${document.getElementById('target-language').options[document.getElementById('target-language').selectedIndex].text}...</div>
        </div>
    `;
    
    try {
        const response = await fetch(`${API_URL}/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                target_lang: targetLang
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.translated_text) {
            // Check if translation contains error message
            if (data.translated_text.includes('Translation Service Unavailable') || 
                data.translated_text.includes('[Translation Error:')) {
                displayTranslationError(data.translated_text);
            } else {
                displayTranslation(data.translated_text, data.target_language, text);
            }
        } else {
            displayTranslationError('Translation failed. Please check your internet connection and try again.');
        }
    } catch (error) {
        console.error('Translation error:', error);
        displayTranslationError('Network error. Please check your internet connection and try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Display Translation Result
function displayTranslation(translatedText, targetLanguage, originalText) {
    const resultDiv = document.getElementById('translation-result');
    resultDiv.style.display = 'block';
    
    // Escape quotes for onclick function
    const escapedText = translatedText.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, '\\n');
    
    resultDiv.innerHTML = `
        <h3>✅ Translation Successful</h3>
        
        <div class="language-result-item" style="margin-bottom: 16px;">
            <div class="language-result-label">Original Text:</div>
            <div class="language-result-value" style="font-size: 14px; line-height: 1.6; padding: 12px; background: var(--card-bg); border-radius: 8px; color: var(--text-secondary); white-space: pre-wrap;">
                ${originalText}
            </div>
        </div>
        
        <div class="language-result-item">
            <div class="language-result-label">Translated to ${targetLanguage}:</div>
            <div class="language-result-value" style="font-size: 16px; line-height: 1.8; padding: 16px; background: var(--card-bg); border-radius: 8px; border-left: 4px solid #22c55e; white-space: pre-wrap; font-weight: 500;">
                ${translatedText}
            </div>
        </div>
        
        <div style="display: flex; gap: 10px; margin-top: 16px;">
            <button class="btn btn-secondary btn-sm" onclick="copyTranslation('${escapedText}')" style="flex: 1;">
                📋 Copy Translation
            </button>
            <button class="btn btn-secondary btn-sm" onclick="useTranslationInAnalyzer('${escapedText}')" style="flex: 1;">
                ✅ Use in Analyzer
            </button>
        </div>
    `;
}

// Display Translation Error
function displayTranslationError(errorMessage) {
    const resultDiv = document.getElementById('translation-result');
    resultDiv.style.display = 'block';
    
    resultDiv.innerHTML = `
        <div style="padding: 20px; background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; border-radius: 12px;">
            <h3 style="color: #ef4444; margin-bottom: 12px;">❌ Translation Failed</h3>
            <div style="color: var(--text-secondary); line-height: 1.6; white-space: pre-wrap;">
                ${errorMessage}
            </div>
            <div style="margin-top: 16px; padding: 12px; background: var(--card-bg); border-radius: 8px; font-size: 14px;">
                <strong>💡 Troubleshooting Tips:</strong><br>
                • Check your internet connection<br>
                • Try a shorter text<br>
                • Wait a moment and try again<br>
                • Make sure the text is in a supported language
            </div>
        </div>
    `;
}

// Copy Translation
function copyTranslation(text) {
    // Unescape the text
    const unescapedText = text.replace(/\\'/g, "'").replace(/\\n/g, '\n');
    navigator.clipboard.writeText(unescapedText).then(() => {
        alert('✅ Translation copied to clipboard!');
    }).catch(err => {
        console.error('Copy failed:', err);
        alert('Failed to copy. Please select and copy manually.');
    });
}

// Use Translation in Analyzer
function useTranslationInAnalyzer(text) {
    // Unescape the text
    const unescapedText = text.replace(/\\'/g, "'").replace(/\\n/g, '\n');
    
    // Set the translated text in the analyzer
    document.getElementById('email-input').value = unescapedText;
    
    // Switch to analyzer view
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelector('[data-view="analyzer"]').classList.add('active');
    document.getElementById('analyzer-view').classList.add('active');
    
    // Scroll to input smoothly
    setTimeout(() => {
        document.getElementById('email-input').scrollIntoView({ behavior: 'smooth', block: 'start' });
        document.getElementById('email-input').focus();
    }, 100);
}

// Get Cultural Tips
document.getElementById('get-cultural-tips-btn').addEventListener('click', async () => {
    const langCode = document.getElementById('cultural-language').value;
    
    const btn = document.getElementById('get-cultural-tips-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/cultural-tips`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lang_code: langCode })
        });
        
        const data = await response.json();
        
        if (data.success && data.tips) {
            displayCulturalTips(data.language, data.tips);
        } else {
            alert('Failed to get cultural tips. Please try again.');
        }
    } catch (error) {
        console.error('Cultural tips error:', error);
        alert('Failed to get cultural tips. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Display Cultural Tips
function displayCulturalTips(language, tips) {
    const resultDiv = document.getElementById('cultural-tips-result');
    resultDiv.style.display = 'block';
    
    resultDiv.innerHTML = `
        <h3>🌍 Cultural Communication Tips for ${language}</h3>
        
        <div class="cultural-tip-card">
            <strong>📊 Formality Level:</strong>
            <p>${tips.formality}</p>
        </div>
        
        <div class="cultural-tip-card">
            <strong>👋 Greeting:</strong>
            <p>${tips.greeting}</p>
        </div>
        
        <div class="cultural-tip-card">
            <strong>✍️ Closing:</strong>
            <p>${tips.closing}</p>
        </div>
        
        <div class="cultural-tip-card">
            <strong>💡 Communication Tips:</strong>
            <p>${tips.tips}</p>
        </div>
    `;
}

// Analyze Localized Tone
document.getElementById('analyze-localized-btn').addEventListener('click', async () => {
    const text = document.getElementById('localized-text').value.trim();
    const langCode = document.getElementById('localized-language').value;
    
    if (!text) {
        alert('Please enter text to analyze');
        return;
    }
    
    const btn = document.getElementById('analyze-localized-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/analyze-tone-localized`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                lang_code: langCode
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.tone_analysis) {
            displayLocalizedToneAnalysis(data.tone_analysis, data.formality);
        } else {
            alert('Tone analysis failed. Please try again.');
        }
    } catch (error) {
        console.error('Localized tone analysis error:', error);
        alert('Failed to analyze tone. Please try again.');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});

// Display Localized Tone Analysis
function displayLocalizedToneAnalysis(toneAnalysis, formality) {
    const resultDiv = document.getElementById('localized-analysis-result');
    resultDiv.style.display = 'block';
    
    // Color code formality level
    let formalityColor = '#667eea';
    if (formality.score >= 7) formalityColor = '#dc2626';
    else if (formality.score >= 5) formalityColor = '#eab308';
    else formalityColor = '#22c55e';
    
    resultDiv.innerHTML = `
        <h3>🎭 Localized Tone Analysis</h3>
        
        <div class="language-result-item">
            <div class="language-result-label">Tone:</div>
            <div class="language-result-value">
                <strong style="font-size: 18px; color: var(--text-primary);">${toneAnalysis.tone}</strong>
                <span style="color: var(--text-secondary);">(Polarity: ${toneAnalysis.polarity})</span>
            </div>
        </div>
        
        <div class="language-result-item">
            <div class="language-result-label">Formality Level:</div>
            <div class="language-result-value">
                <strong style="font-size: 18px; color: ${formalityColor};">${formality.level}</strong>
                <span style="color: var(--text-secondary);">(Score: ${formality.score}/10)</span>
                <div style="margin-top: 8px; padding: 10px; background: var(--card-bg); border-radius: 6px; font-size: 13px;">
                    ${formality.expected_for_culture}
                </div>
            </div>
        </div>
        
        <div class="language-result-item">
            <div class="language-result-label">Cultural Context:</div>
            <div class="language-result-value" style="line-height: 1.8;">
                ${toneAnalysis.cultural_context}
            </div>
        </div>
        
        <div class="cultural-tip-card">
            <strong>💡 Communication Guidelines:</strong>
            <p><strong>Formality:</strong> ${toneAnalysis.tips.formality}</p>
            <p><strong>Greeting:</strong> ${toneAnalysis.tips.greeting}</p>
            <p><strong>Closing:</strong> ${toneAnalysis.tips.closing}</p>
            <p><strong>Tips:</strong> ${toneAnalysis.tips.tips}</p>
        </div>
    `;
}


// ===== REPORTS FUNCTIONALITY =====

let currentReportData = null;

// Generate Report buttons
document.querySelectorAll('.generate-report-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const period = btn.dataset.period;
        const periodLabel = period === 'week' ? 'Weekly' : 'Monthly';
        
        btn.classList.add('loading');
        btn.disabled = true;
        
        try {
            const response = await fetch(`${API_URL}/reports/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: currentUser.id,
                    period: period
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.summary && data.summary.total_emails_analyzed > 0) {
                currentReportData = data;
                displayReport(data);
            }
        } catch (error) {
            console.error('Report generation error:', error);
        } finally {
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    });
});

// Display Report
function displayReport(report) {
    console.log('📊 Displaying report:', report);
    
    const displaySection = document.getElementById('report-display-section');
    displaySection.style.display = 'block';
    
    // Update title
    document.getElementById('report-title').textContent = report.period_label + ' Report';
    
    // Display Summary Statistics
    displayReportStats(report.summary);
    
    // Display Improvements
    displayReportImprovements(report.most_improved_areas);
    
    // Display Areas Needing Work
    displayReportNeedsWork(report.areas_needing_work);
    
    // Display Trends
    displayReportTrends(report.writing_trends);
    
    // Display Insights
    displayReportInsights(report.insights);
    
    // Scroll to report
    displaySection.scrollIntoView({ behavior: 'smooth' });
}

// Display Summary Statistics
function displayReportStats(summary) {
    const statsGrid = document.getElementById('report-stats-grid');
    statsGrid.innerHTML = '';
    
    const stats = [
        { label: 'Total Emails', value: summary.total_emails_analyzed, suffix: '' },
        { label: 'Avg Professionalism', value: summary.average_professionalism, suffix: '/10', score: summary.average_professionalism * 10 },
        { label: 'Avg Overall Quality', value: summary.average_overall_quality, suffix: '/100', score: summary.average_overall_quality },
        { label: 'Avg Readability', value: summary.average_readability, suffix: '/100', score: summary.average_readability },
        { label: 'Avg Clarity', value: summary.average_clarity, suffix: '/100', score: summary.average_clarity },
        { label: 'Avg Engagement', value: summary.average_engagement, suffix: '/100', score: summary.average_engagement }
    ];
    
    stats.forEach(stat => {
        const statItem = document.createElement('div');
        statItem.className = 'report-stat-item';
        
        let scoreClass = '';
        if (stat.score !== undefined) {
            if (stat.score >= 80) scoreClass = 'excellent';
            else if (stat.score >= 60) scoreClass = 'good';
            else if (stat.score >= 40) scoreClass = 'fair';
            else scoreClass = 'poor';
        }
        
        statItem.innerHTML = `
            <div class="report-stat-label">${stat.label}</div>
            <div class="report-stat-value ${scoreClass}">${stat.value}${stat.suffix}</div>
        `;
        
        statsGrid.appendChild(statItem);
    });
}

// Display Improvements
function displayReportImprovements(improvements) {
    const container = document.getElementById('report-improvements');
    container.innerHTML = '';
    
    if (!improvements || improvements.length === 0) {
        container.innerHTML = '<div class="report-empty-state"><p>No improvements detected yet. Keep analyzing emails!</p></div>';
        return;
    }
    
    improvements.forEach(item => {
        const improvementItem = document.createElement('div');
        improvementItem.className = 'report-improvement-item';
        
        let details = '';
        if (item.improvement) details += `<div class="report-item-detail">✓ ${item.improvement}</div>`;
        if (item.achievement) details += `<div class="report-item-detail">✓ ${item.achievement}</div>`;
        if (item.score) details += `<div class="report-item-detail">Score: ${item.score}</div>`;
        
        improvementItem.innerHTML = `
            <div class="report-item-title">+ ${item.area}</div>
            ${details}
            <div class="report-item-description">${item.description}</div>
        `;
        
        container.appendChild(improvementItem);
    });
}

// Display Areas Needing Work
function displayReportNeedsWork(needsWork) {
    const container = document.getElementById('report-needs-work');
    container.innerHTML = '';
    
    if (!needsWork || needsWork.length === 0) {
        container.innerHTML = '<div class="report-empty-state"><p>Great job! No major areas of concern.</p></div>';
        return;
    }
    
    needsWork.forEach(item => {
        const needsWorkItem = document.createElement('div');
        needsWorkItem.className = 'report-needs-work-item';
        
        let details = '';
        if (item.decline) details += `<div class="report-item-detail">⚠ ${item.decline}</div>`;
        if (item.issue) details += `<div class="report-item-detail">⚠ ${item.issue}</div>`;
        if (item.score) details += `<div class="report-item-detail">Score: ${item.score}</div>`;
        
        needsWorkItem.innerHTML = `
            <div class="report-item-title">! ${item.area}</div>
            ${details}
            <div class="report-item-description">${item.description}</div>
        `;
        
        container.appendChild(needsWorkItem);
    });
}

// Display Trends
function displayReportTrends(trends) {
    const container = document.getElementById('report-trends');
    container.innerHTML = '';
    
    const trendItems = [
        { label: 'Professionalism Trend', value: `${trends.professionalism_trend.direction} (${trends.professionalism_trend.change > 0 ? '+' : ''}${trends.professionalism_trend.change})`, class: trends.professionalism_trend.direction },
        { label: 'Overall Quality Trend', value: `${trends.overall_quality_trend.direction} (${trends.overall_quality_trend.change > 0 ? '+' : ''}${trends.overall_quality_trend.change})`, class: trends.overall_quality_trend.direction },
        { label: 'Most Used Tone', value: trends.most_used_tone, class: 'stable' },
        { label: 'Most Common Intent', value: trends.most_common_intent, class: 'stable' },
        { label: 'Dominant Sentiment', value: trends.dominant_sentiment, class: 'stable' },
        { label: 'Typical Priority', value: trends.typical_priority, class: 'stable' }
    ];
    
    trendItems.forEach(item => {
        const trendItem = document.createElement('div');
        trendItem.className = 'report-trend-item';
        trendItem.innerHTML = `
            <div class="report-trend-label">${item.label}:</div>
            <div class="report-trend-value ${item.class}">${item.value}</div>
        `;
        container.appendChild(trendItem);
    });
}

// Display Insights
function displayReportInsights(insights) {
    const container = document.getElementById('report-insights');
    container.innerHTML = '';
    
    if (!insights || insights.length === 0) {
        container.innerHTML = '<div class="report-empty-state"><p>Continue analyzing emails to generate insights.</p></div>';
        return;
    }
    
    insights.forEach(insight => {
        const insightItem = document.createElement('div');
        insightItem.className = 'report-insight-item';
        insightItem.textContent = insight;
        container.appendChild(insightItem);
    });
}

// Download Report PDF
document.getElementById('download-report-pdf-btn').addEventListener('click', async () => {
    if (!currentReportData) {
        alert('No report data available to download. Please generate a report first.');
        return;
    }
    
    const btn = document.getElementById('download-report-pdf-btn');
    btn.classList.add('loading');
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/reports/download-pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                report_data: currentReportData,
                user_email: currentUser.email
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error response:', errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }
        
        const blob = await response.blob();
        
        if (blob.size === 0) {
            throw new Error('Received empty PDF file');
        }
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `CommAI_${currentReportData.period_label.replace(/ /g, '_')}_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('PDF download error:', error);
        alert(`Failed to download PDF report: ${error.message}`);
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
});


// ===== FLOATING CHATBOT BUTTON =====

// Floating chatbot button - opens chatbot view
document.getElementById('floating-chatbot-btn').addEventListener('click', () => {
    // Switch to chatbot view
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    
    // Show chatbot view
    document.getElementById('chatbot-view').classList.add('active');
    
    // Focus on chat input
    setTimeout(() => {
        document.getElementById('chat-input').focus();
    }, 100);
});
