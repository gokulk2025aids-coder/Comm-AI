# CommAI - Advanced AI Email Analyzer

A production-ready AI-powered web application for comprehensive email analysis with intelligent chatbot, secure authentication, animated UI, and professional PDF reports.

---

## Features

### Multi-Language Support
- **Language Detection** — Automatically detect email language from 13+ languages
- **Translation** — Translate emails between English, Spanish, French, German, Italian, Portuguese, Dutch, Japanese, Chinese, Arabic, Hindi, Russian, Tamil
- **Cultural Communication Tips** — Get culturally appropriate writing guidance per language
- **Localized Tone Analysis** — Tone analysis adjusted for cultural context
- **Formality Assessment** — Understand formality levels appropriate for each culture

### Authentication System
- **OTP Login** — Email-based one-time password authentication (hashed with bcrypt)
- **Password Login** — Traditional email/password authentication
- **Sign Up** — New user registration with secure bcrypt password hashing
- **Session Management** — Persistent user sessions

### Email Analysis Engine
- **Summary** — 2-3 line overview of email content
- **Tone Analysis** — Formal, Friendly, Negative, Apologetic, Neutral (with reasoning)
- **Intent Detection** — Request, Inquiry, Complaint, Follow-up, Confirmation, Meeting Request, Thank You (with confidence %)
- **Sentiment Analysis** — Positive/Neutral/Negative with polarity score (-1 to +1)
- **Emotion Detection** — Happy, Angry, Sad, Anxious, Positive, Negative, Neutral
- **Key Points Extraction** — Bullet-point summary of main topics
- **Action Items** — Identified tasks with responsibility assignment
- **Priority Level** — Critical/High/Medium/Low with reasoning
- **Professionalism Score** — Detailed 0-10 rating with breakdown
- **Email Quality Scores** — Overall, Readability, Clarity, Engagement, Professional Impact (0-100)
- **Grammar & Structure Analysis** — Identifies issues and provides corrections
- **Suggested Reply** — Professional response template
- **Email Improvement Suggestions** — Rewritten version of your email

### Bulk Email Analysis
- **Batch Processing** — Upload multiple emails via file or manual entry
- **Comprehensive Scoring** — All emails scored across 5 quality dimensions
- **Interactive Charts** — Visual comparison with Chart.js (professionalism, clarity, engagement)
- **Smart Pagination** — 10 emails per page
- **Detailed Results Table** — Complete analysis for each email
- **Export Options** — CSV and Excel export
- **Side-by-Side Comparison** — Compare multiple emails in modal view
- **Progress Tracking** — Real-time analysis progress indicator

### Tone Adjuster
- **Casual to Formal** — Convert informal writing to professional tone
- **Aggressive to Diplomatic** — Soften harsh language
- **Formality Slider** — Fine-tune formality level (0-100)
- **Live Preview** — See changes before applying

### Subject Line Analyzer
- **Score & Analysis** — Rate your subject line effectiveness
- **Improvement Suggestions** — Get actionable recommendations
- **A/B Test Variations** — Generate multiple subject line options

### Email Length Optimizer
- **Length Analysis** — Check if your email is too short, ideal, or too long
- **Summarize** — Condense long emails automatically
- **Expand** — Flesh out brief emails with more detail
- **Smart Optimize** — Auto-detect and apply the best action

### Best Practices Library
- Curated email writing guidelines
- Searchable by category or keyword
- Covers tone, structure, formatting, and more

### Email Writing Quiz
- Test your email communication knowledge
- Instant feedback with explanations
- Scored results with category breakdown

### AI Chatbot Assistant
Context-aware chatbot covering:
- Professional email writing tips
- Cultural communication styles (US, UK, India, Japan, Germany, Brazil)
- Email types (apology, follow-up, request, complaint, meeting, thank you)
- Tone, sentiment, grammar guidance
- Subject line and formatting best practices

**Chatbot Modes:**
- **Anthropic Claude** — When `ANTHROPIC_API_KEY` is set
- **OpenAI GPT** — When `OPENAI_API_KEY` is set
- **Built-in Intelligence** — Works with no API key

### PDF Report Generation
- Original email text + full analysis results
- Visual formatting with colors and structured sections
- Weekly/Monthly progress reports as downloadable PDFs

### History & Reports
- Per-user analysis history with timestamps
- Weekly/Monthly report generation
- Score trends, writing patterns, key insights
- Most improved areas and areas needing work

---

## Project Structure

```
CommAi/
├── backend/
│   ├── main.py                  # FastAPI server & all API endpoints
│   ├── database.py              # SQLite database management
│   ├── auth.py                  # Authentication (OTP & password)
│   ├── nlp_engine.py            # Core email analysis engine
│   ├── chatbot.py               # AI chatbot with context awareness
│   ├── pdf_generator.py         # Email analysis PDF reports
│   ├── report_pdf_generator.py  # Weekly/monthly PDF reports
│   ├── reports_generator.py     # Report data aggregation
│   ├── tone_adjuster.py         # Tone conversion engine
│   ├── email_length_optimizer.py# Email length analysis & optimization
│   ├── subject_line_analyzer.py # Subject line scoring & suggestions
│   ├── language_support.py      # Language detection & translation
│   ├── best_practices.py        # Best practices library
│   ├── email_quiz.py            # Quiz questions & scoring
│   └── test_*.py                # Test files
│
├── frontend/
│   ├── index.html               # Main application
│   ├── app.css                  # Application styles
│   ├── app.js                   # Application logic
│   ├── login.html               # Login page
│   ├── login.css                # Login styles
│   ├── login.js                 # Login logic
│   ├── best-practices.html      # Best practices page
│   ├── quiz.html                # Quiz page
│   ├── reports_view.html        # Reports page
│   ├── email-templates.js       # Email template library
│   └── chart.min.js             # Chart.js (local copy)
│
├── docs/                        # All documentation & guides
├── .env                         # Environment variables (not committed)
├── .env.example                 # Environment variable template
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
├── run_tests.bat                # Run all tests (Windows)
├── start.bat                    # Windows launcher
└── README.md                    # This file
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge)

### Step 1: Install Dependencies

```cmd
pip install -r requirements.txt
python -m textblob.download_corpora
```

### Step 2: Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```cmd
copy .env.example .env
```

Key settings in `.env`:

```env
# Required for real OTP emails (optional - dev mode prints OTP to terminal)
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-digit-app-password

# Optional AI chatbot (leave empty to use built-in chatbot)
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key

# CORS - set to your frontend URL in production
ALLOWED_ORIGINS=http://localhost:8000
```

**To get a Gmail App Password:**
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification
3. Search "App Passwords" → Generate
4. Copy the 16-digit password

### Step 3: Run the Application

**Windows:**
```cmd
start.bat
```

**Mac/Linux:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Step 4: Open in Browser

```
http://localhost:8000
```

---

## How to Use

### Login / Signup
- Choose OTP Login or Password Login
- OTP mode: Enter email → check terminal (dev) or inbox → enter the 6-digit code
- Password mode: Enter credentials or create a new account

### Analyze an Email
- Paste your email in the text area
- Click "Analyze Email"
- View the full analysis breakdown
- Download a PDF report if needed

### Bulk Analysis
- Go to the Bulk Analysis section
- Paste or upload multiple emails
- View interactive charts and comparison table
- Export results as CSV or Excel

### Tone Adjuster
- Paste your email text
- Choose conversion type (casual→formal, aggressive→diplomatic, or use the slider)
- Preview the adjusted version instantly

### Subject Line Analyzer
- Enter your subject line
- Get a score, suggestions, and A/B test variations

### AI Chatbot
- Click "AI Chatbot" in the sidebar
- Ask anything about email writing, tone, grammar, or communication
- Responses are context-aware across the conversation

### Weekly / Monthly Reports
- Go to Reports in the sidebar
- Select Weekly or Monthly period
- View trends, scores, and AI-generated insights
- Download as PDF

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, FastAPI, Uvicorn |
| NLP Engine | TextBlob, Custom Rule-Based Analysis |
| AI Chatbot | Anthropic Claude / OpenAI GPT / Built-in |
| PDF Generation | fpdf2 |
| Database | SQLite |
| Authentication | bcrypt (passwords & OTPs), Gmail SMTP |
| Rate Limiting | slowapi |
| Language Support | langdetect, deep-translator |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js |
| UI Design | Glassmorphism, Gradient Animations |

---

## Security

- Passwords hashed with **bcrypt**
- OTPs hashed with **bcrypt** before database storage
- OTP expiration after **10 minutes**
- CORS restricted to configured `ALLOWED_ORIGINS`
- Rate limiting on all API endpoints
- Input validation via Pydantic models
- SQL injection prevention via parameterized queries
- API keys loaded from environment variables only

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/request-otp` | POST | Request OTP for email |
| `/api/auth/verify-otp` | POST | Verify OTP and login |
| `/api/auth/signup` | POST | Create new account |
| `/api/auth/login` | POST | Password-based login |
| `/api/analyze` | POST | Analyze email text |
| `/api/chat` | POST | Chat with AI assistant |
| `/api/history` | POST | Get user's analysis history |
| `/api/history/{id}` | DELETE | Delete a history item |
| `/api/generate-pdf` | POST | Generate analysis PDF |
| `/api/chat-history/{user_id}` | GET | Get chat history |
| `/api/detect-language` | POST | Detect email language |
| `/api/translate` | POST | Translate email text |
| `/api/cultural-tips` | POST | Get cultural communication tips |
| `/api/analyze-tone-localized` | POST | Tone analysis with cultural context |
| `/api/adjust-tone` | POST | Convert email tone |
| `/api/optimize-length` | POST | Analyze or optimize email length |
| `/api/analyze-subject` | POST | Score and improve subject lines |
| `/api/best-practices` | GET | Get best practices library |
| `/api/best-practices/search` | GET | Search best practices |
| `/api/quiz/questions` | GET | Get quiz questions |
| `/api/quiz/submit` | POST | Submit quiz answers |
| `/api/reports/generate` | POST | Generate weekly/monthly report |
| `/api/reports/download-pdf` | POST | Download report as PDF |
| `/api/health` | GET | Health check |

---

## Analysis Output Format

```json
{
  "analysis": {
    "summary": "Brief overview...",
    "tone": "Formal",
    "tone_reasoning": "Uses professional language...",
    "intent": "Request",
    "confidence": "85%",
    "sentiment": "Positive",
    "polarity": 0.45,
    "emotion": "Neutral",
    "key_points": ["Point 1", "Point 2"],
    "action_items": [
      { "action": "Send report", "responsibility": "Recipient" }
    ],
    "priority": "High",
    "priority_reason": "Contains urgent indicators",
    "suggested_reply": "Professional response template..."
  }
}
```

---

## Troubleshooting

**OTP not received in email:**
- In dev mode (no Gmail configured), the OTP is printed directly to the terminal window — check there
- If using Gmail, verify your App Password is correct and 2-Step Verification is enabled
- Check your spam/junk folder

**Port 8000 already in use:**
- Edit `start.bat` and change `--port 8000` to `--port 8001`
- Or find and stop the process using port 8000:
  ```cmd
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

**Module not found error:**
- Run `pip install -r requirements.txt` from the project root
- Ensure you are using Python 3.10 or higher: `python --version`
- If TextBlob errors appear: `python -m textblob.download_corpora`

**bcrypt / password login not working:**
- If you had an existing `commai.db` from before bcrypt was added, delete it and restart — the database will be recreated automatically
- New accounts created after the fix will work correctly

**Database errors:**
- Delete `commai.db` from the project root and restart the server
- The database schema is recreated automatically on startup

**Translation not working:**
- Run: `pip install deep-translator langdetect`
- Ensure you have an active internet connection (translation uses an external API)

**Charts not displaying in bulk analysis:**
- The project includes a local `chart.min.js` in the frontend folder — no internet required
- If charts still don't show, hard-refresh the browser (Ctrl+Shift+R)

**PDF download is blank or fails:**
- Ensure `fpdf2` is installed: `pip install fpdf2`
- Check the terminal for error details

---

## Running Tests

```cmd
run_tests.bat
```

Or manually:
```cmd
cd backend
pytest
```

---

## License

This project is open source and available for educational and commercial use.

---

Built with FastAPI, TextBlob, bcrypt, and modern web technologies.
