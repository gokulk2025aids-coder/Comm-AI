from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
import os
import logging
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from auth import AuthService
from nlp_engine import EmailAnalyzer
from chatbot import Chatbot
from pdf_generator import PDFGenerator
from database import Database
from tone_adjuster import ToneAdjuster
from email_length_optimizer import EmailLengthOptimizer
from subject_line_analyzer import SubjectLineAnalyzer
from language_support import LanguageSupport
from reports_generator import ReportsGenerator
from report_pdf_generator import ReportPDFGenerator
from best_practices import get_all_practices, get_by_category, search_practices
from email_quiz import get_all_questions, get_random_questions, check_answer, calculate_score

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('commai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Check if in testing mode
TESTING_MODE = os.getenv("TESTING") == "true"

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CommAI Email Analyzer")

# Only enable rate limiting in production
if not TESTING_MODE:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Mount frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Initialize services
auth_service = AuthService()
email_analyzer = EmailAnalyzer()
chatbot = Chatbot()
pdf_generator = PDFGenerator()
db = Database()
tone_adjuster = ToneAdjuster()
length_optimizer = EmailLengthOptimizer()
subject_analyzer = SubjectLineAnalyzer()
language_support = LanguageSupport()
reports_generator = ReportsGenerator(db)
report_pdf_generator = ReportPDFGenerator()

# Helper function for conditional rate limiting
def rate_limit(limit_string):
    def decorator(func):
        if not TESTING_MODE:
            return limiter.limit(limit_string)(func)
        return func
    return decorator

# Models with validation
class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str
    
    @validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('OTP must be 6 digits')
        return v

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AnalyzeRequest(BaseModel):
    email_text: str
    user_id: int
    
    @validator('email_text')
    def validate_email_text(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Email text must be at least 10 characters')
        if len(v) > 50000:
            raise ValueError('Email text too long (max 50000 characters)')
        return v

class ChatRequest(BaseModel):
    message: str
    user_id: int
    
    @validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message too long (max 5000 characters)')
        return v

class HistoryRequest(BaseModel):
    user_id: int

class ToneAdjustRequest(BaseModel):
    text: str
    conversion_type: str
    formality_level: Optional[int] = 50
    
    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Text must be at least 5 characters')
        if len(v) > 50000:
            raise ValueError('Text too long (max 50000 characters)')
        return v
    
    @validator('conversion_type')
    def validate_conversion_type(cls, v):
        valid_types = ['casual_to_formal', 'aggressive_to_diplomatic', 'formality_slider']
        if v not in valid_types:
            raise ValueError(f'Invalid conversion type. Must be one of: {valid_types}')
        return v

class LengthOptimizeRequest(BaseModel):
    text: str
    action: str  # 'analyze', 'summarize', 'expand', 'optimize'
    
    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('Text must be at least 5 characters')
        if len(v) > 50000:
            raise ValueError('Text too long (max 50000 characters)')
        return v
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['analyze', 'summarize', 'expand', 'optimize']
        if v not in valid_actions:
            raise ValueError(f'Invalid action. Must be one of: {valid_actions}')
        return v

class SubjectLineRequest(BaseModel):
    subject: str
    action: str  # 'analyze', 'suggest', 'ab_test'
    
    @validator('subject')
    def validate_subject(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Subject line cannot be empty')
        if len(v) > 200:
            raise ValueError('Subject line too long (max 200 characters)')
        return v
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['analyze', 'suggest', 'ab_test']
        if v not in valid_actions:
            raise ValueError(f'Invalid action. Must be one of: {valid_actions}')
        return v

class LanguageDetectRequest(BaseModel):
    text: str
    
    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Text cannot be empty')
        if len(v) > 50000:
            raise ValueError('Text too long (max 50000 characters)')
        return v

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    
    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Text cannot be empty')
        if len(v) > 50000:
            raise ValueError('Text too long (max 50000 characters)')
        return v
    
    @validator('target_lang')
    def validate_target_lang(cls, v):
        valid_langs = ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ja', 'zh', 'ar', 'hi', 'ru', 'ta']
        if v not in valid_langs:
            raise ValueError(f'Invalid target language. Must be one of: {valid_langs}')
        return v

class CulturalTipsRequest(BaseModel):
    lang_code: str
    
    @validator('lang_code')
    def validate_lang_code(cls, v):
        valid_langs = ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ja', 'zh', 'ar', 'hi', 'ru', 'ta']
        if v not in valid_langs:
            raise ValueError(f'Invalid language code. Must be one of: {valid_langs}')
        return v

# Routes
@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "login.html"))

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "CommAI Email Analyzer",
        "features": {
            "email_analysis": True,
            "chatbot": True,
            "tone_adjuster": True,
            "bulk_analysis": True,
            "templates": True
        }
    }

@app.post("/api/auth/request-otp")
@rate_limit("5/minute")
async def request_otp(request: Request, otp_request: OTPRequest):
    try:
        logger.info(f"OTP request received for: {otp_request.email}")
        success = auth_service.request_otp(otp_request.email)
        if success:
            logger.info(f"OTP sent successfully for: {otp_request.email}")
            return {"success": True, "message": "OTP sent successfully"}
        logger.error(f"Failed to send OTP for: {otp_request.email}")
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    except ValueError as e:
        logger.warning(f"Invalid OTP request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP request error for {otp_request.email}: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/auth/verify-otp")
@rate_limit("10/minute")
async def verify_otp(request: Request, verify_request: OTPVerify):
    try:
        user = auth_service.verify_otp_login(verify_request.email, verify_request.otp)
        if user:
            logger.info(f"OTP verified for: {verify_request.email}")
            return {"success": True, "user": user}
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    except ValueError as e:
        logger.warning(f"Invalid OTP verification: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/signup")
@rate_limit("3/minute")
async def signup(request: Request, signup_request: SignupRequest):
    try:
        user = auth_service.signup(signup_request.email, signup_request.password)
        if user:
            logger.info(f"User signed up: {signup_request.email}")
            return {"success": True, "user": user}
        raise HTTPException(status_code=400, detail="Email already exists")
    except ValueError as e:
        logger.warning(f"Invalid signup: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/auth/login")
@rate_limit("10/minute")
async def login(request: Request, login_request: LoginRequest):
    try:
        logger.info(f"Login attempt for: {login_request.email}")
        user = auth_service.login(login_request.email, login_request.password)
        if user:
            logger.info(f"User logged in successfully: {login_request.email}")
            return {"success": True, "user": user}
        logger.warning(f"Login failed - invalid credentials: {login_request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except ValueError as e:
        logger.warning(f"Invalid login request for {login_request.email}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {login_request.email}: {e}")
        logger.error(f"Error details: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/analyze")
@rate_limit("20/minute")
async def analyze_email(request: Request, analyze_request: AnalyzeRequest):
    try:
        analysis = email_analyzer.analyze(analyze_request.email_text)
        
        # Save to database
        analysis_id = db.save_analysis(analyze_request.user_id, analyze_request.email_text, analysis)
        
        logger.info(f"Email analyzed for user {analyze_request.user_id}")
        return {
            "success": True,
            "analysis": analysis,
            "analysis_id": analysis_id
        }
    except ValueError as e:
        logger.warning(f"Invalid analysis request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze email")

@app.post("/api/chat")
@rate_limit("30/minute")
async def chat(request: Request, chat_request: ChatRequest):
    try:
        # Get chat history for context
        context = chatbot.get_chat_history(chat_request.user_id)
        
        response = chatbot.get_response(chat_request.message, chat_request.user_id, context)
        
        logger.info(f"Chat response generated for user {chat_request.user_id}")
        return {
            "success": True,
            "response": response,
            "context_used": len(context) > 0
        }
    except ValueError as e:
        logger.warning(f"Invalid chat request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@app.post("/api/history")
@rate_limit("30/minute")
async def get_history(request: Request, history_request: HistoryRequest):
    try:
        analyses = db.get_user_analyses(history_request.user_id)
        return {
            "success": True,
            "history": analyses
        }
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@app.delete("/api/history/{analysis_id}")
@rate_limit("30/minute")
async def delete_history(request: Request, analysis_id: int, user_id: int):
    try:
        success = db.delete_analysis(analysis_id, user_id)
        if success:
            return {"success": True, "message": "Analysis deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete history item")

@app.post("/api/generate-pdf")
@rate_limit("10/minute")
async def generate_pdf(request: Request, pdf_request: dict):
    try:
        logger.info(f"PDF generation request received: {pdf_request.keys()}")
        
        analysis = pdf_request.get("analysis")
        email_text = pdf_request.get("email_text")
        user_email = pdf_request.get("user_email")
        theme = pdf_request.get("theme", "dark")  # Default to dark
        
        logger.info(f"Analysis present: {analysis is not None}, Email text present: {email_text is not None}, User email: {user_email}")
        
        if not analysis or not email_text:
            logger.error("Missing analysis or email_text")
            raise HTTPException(status_code=400, detail="Missing required data")
        
        logger.info("Calling PDF generator...")
        pdf_bytes = pdf_generator.generate_report(analysis, email_text, user_email, theme)
        
        # Ensure pdf_bytes is proper bytes object
        if isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)
        elif isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
        
        logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        
        from datetime import datetime
        filename = f"email_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF Generation Error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.get("/api/chat-history/{user_id}")
@rate_limit("30/minute")
async def get_chat_history(request: Request, user_id: int):
    try:
        history = chatbot.get_chat_history(user_id)
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        logger.error(f"Chat history fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@app.post("/api/adjust-tone")
@rate_limit("30/minute")
async def adjust_tone(request: Request, adjust_request: ToneAdjustRequest):
    try:
        adjusted_text = tone_adjuster.preview_tone(
            adjust_request.text,
            adjust_request.conversion_type,
            adjust_request.formality_level
        )
        
        logger.info(f"Tone adjusted: {adjust_request.conversion_type}")
        return {
            "success": True,
            "adjusted_text": adjusted_text,
            "conversion_type": adjust_request.conversion_type
        }
    except ValueError as e:
        logger.warning(f"Invalid tone adjustment request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Tone adjustment error: {e}")
        raise HTTPException(status_code=500, detail="Failed to adjust tone")

@app.post("/api/optimize-length")
@rate_limit("30/minute")
async def optimize_length(request: Request, optimize_request: LengthOptimizeRequest):
    try:
        if optimize_request.action == 'analyze':
            result = length_optimizer.analyze_length(optimize_request.text)
            logger.info(f"Length analyzed: {result['word_count']} words, status: {result['status']}")
            return {
                "success": True,
                "analysis": result
            }
        elif optimize_request.action == 'summarize':
            summarized = length_optimizer.summarize_email(optimize_request.text)
            analysis = length_optimizer.analyze_length(summarized)
            logger.info(f"Email summarized from {len(optimize_request.text.split())} to {analysis['word_count']} words")
            return {
                "success": True,
                "optimized_text": summarized,
                "analysis": analysis
            }
        elif optimize_request.action == 'expand':
            expanded = length_optimizer.expand_email(optimize_request.text)
            analysis = length_optimizer.analyze_length(expanded)
            logger.info(f"Email expanded from {len(optimize_request.text.split())} to {analysis['word_count']} words")
            return {
                "success": True,
                "optimized_text": expanded,
                "analysis": analysis
            }
        elif optimize_request.action == 'optimize':
            result = length_optimizer.get_optimal_suggestion(optimize_request.text)
            logger.info(f"Email optimized: {result['action']} action taken")
            return {
                "success": True,
                "result": result
            }
    except ValueError as e:
        logger.warning(f"Invalid length optimization request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Length optimization error: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize email length")

@app.post("/api/analyze-subject")
@rate_limit("30/minute")
async def analyze_subject(request: Request, subject_request: SubjectLineRequest):
    try:
        if subject_request.action == 'analyze':
            result = subject_analyzer.analyze_subject_line(subject_request.subject)
            logger.info(f"Subject analyzed: score {result.get('score', 0)}")
            return {
                "success": True,
                "analysis": result
            }
        elif subject_request.action == 'suggest':
            result = subject_analyzer.suggest_improvements(subject_request.subject)
            logger.info(f"Subject suggestions generated")
            return {
                "success": True,
                "suggestions": result
            }
        elif subject_request.action == 'ab_test':
            result = subject_analyzer.generate_ab_tests(subject_request.subject)
            logger.info(f"A/B test variations generated")
            return {
                "success": True,
                "ab_tests": result
            }
    except ValueError as e:
        logger.warning(f"Invalid subject line request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Subject line analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze subject line")

@app.post("/api/detect-language")
@rate_limit("30/minute")
async def detect_language(request: Request, detect_request: LanguageDetectRequest):
    try:
        result = language_support.detect_language(detect_request.text)
        logger.info(f"Language detected: {result['name']}")
        return {
            "success": True,
            "language": result
        }
    except ValueError as e:
        logger.warning(f"Invalid language detection request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect language")

@app.post("/api/translate")
@rate_limit("20/minute")
async def translate(request: Request, translate_request: TranslateRequest):
    try:
        translated = language_support.translate_text(translate_request.text, translate_request.target_lang)
        logger.info(f"Text translated to {translate_request.target_lang}")
        return {
            "success": True,
            "translated_text": translated,
            "target_language": language_support.supported_languages.get(translate_request.target_lang)
        }
    except ValueError as e:
        logger.warning(f"Invalid translation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate text")

@app.post("/api/cultural-tips")
@rate_limit("30/minute")
async def get_cultural_tips(request: Request, tips_request: CulturalTipsRequest):
    try:
        tips = language_support.get_cultural_tips(tips_request.lang_code)
        logger.info(f"Cultural tips retrieved for {tips_request.lang_code}")
        return {
            "success": True,
            "language": language_support.supported_languages.get(tips_request.lang_code),
            "tips": tips
        }
    except ValueError as e:
        logger.warning(f"Invalid cultural tips request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Cultural tips error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cultural tips")

@app.post("/api/analyze-tone-localized")
@rate_limit("30/minute")
async def analyze_tone_localized(request: Request, analyze_request: dict):
    try:
        text = analyze_request.get('text')
        lang_code = analyze_request.get('lang_code', 'en')
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = language_support.analyze_tone_localized(text, lang_code)
        formality = language_support.get_formality_level(text, lang_code)
        
        logger.info(f"Localized tone analyzed for {lang_code}")
        return {
            "success": True,
            "tone_analysis": result,
            "formality": formality
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Localized tone analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze tone")

@app.post("/api/reports/generate")
@rate_limit("10/minute")
async def generate_report(request: Request, report_request: dict):
    """Generate weekly or monthly report"""
    try:
        user_id = report_request.get('user_id')
        period = report_request.get('period', 'week')  # 'week' or 'month'
        
        if not user_id:
            logger.error("No user ID provided")
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if period not in ['week', 'month']:
            logger.error(f"Invalid period: {period}")
            raise HTTPException(status_code=400, detail="Period must be 'week' or 'month'")
        
        logger.info(f"Generating {period} report for user {user_id}")
        report = reports_generator.generate_report(user_id, period)
        
        if not report.get('success'):
            logger.warning(f"Report generation returned success=False: {report.get('message')}")
            return report
        
        logger.info(f"Report generated successfully for user {user_id}")
        logger.info(f"Report contains {report.get('summary', {}).get('total_emails_analyzed', 0)} emails")
        return report
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@app.post("/api/reports/download-pdf")
@rate_limit("5/minute")
async def download_report_pdf(request: Request, pdf_request: dict):
    """Download report as PDF"""
    try:
        report_data = pdf_request.get('report_data')
        user_email = pdf_request.get('user_email')
        
        logger.info(f"PDF download request from: {user_email}")
        logger.info(f"Report data present: {report_data is not None}")
        
        if not report_data:
            logger.error("No report data provided")
            raise HTTPException(status_code=400, detail="Report data is required")
        
        if not user_email:
            logger.error("No user email provided")
            raise HTTPException(status_code=400, detail="User email is required")
        
        # Validate report data structure
        required_keys = ['period_label', 'summary']
        for key in required_keys:
            if key not in report_data:
                logger.warning(f"Missing key in report data: {key}")
        
        logger.info(f"Generating PDF report for {user_email}")
        logger.info(f"Report data keys: {list(report_data.keys())}")
        
        pdf_bytes = report_pdf_generator.generate_report_pdf(report_data, user_email)
        
        # Ensure pdf_bytes is proper bytes object
        if isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)
        elif isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
        
        if not pdf_bytes or len(pdf_bytes) == 0:
            logger.error("Generated PDF is empty")
            raise HTTPException(status_code=500, detail="Generated PDF is empty")
        
        from datetime import datetime
        period_label = report_data.get('period_label', 'Report').replace(' ', '_')
        filename = f"CommAI_{period_label}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        logger.info(f"PDF report generated successfully, size: {len(pdf_bytes)} bytes")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF report generation error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

@app.get("/api/best-practices")
@rate_limit("30/minute")
async def get_best_practices(request: Request, category: Optional[str] = None):
    """Get best practices library content"""
    try:
        if category:
            data = get_by_category(category)
            logger.info(f"Best practices fetched for category: {category}")
        else:
            data = get_all_practices()
            logger.info("All best practices fetched")
        
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        logger.error(f"Best practices fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch best practices")

@app.get("/api/best-practices/search")
@rate_limit("30/minute")
async def search_best_practices(request: Request, q: str):
    """Search best practices library"""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        results = search_practices(q)
        logger.info(f"Best practices search for '{q}': {len(results)} results")
        
        return {
            "success": True,
            "query": q,
            "results": results,
            "count": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Best practices search error: {e}")
        raise HTTPException(status_code=500, detail="Failed to search best practices")

@app.get("/api/quiz/questions")
@rate_limit("30/minute")
async def get_quiz_questions(request: Request, count: int = 10):
    """Get quiz questions"""
    try:
        if count <= 0 or count > 20:
            raise HTTPException(status_code=400, detail="Count must be between 1 and 20")
        
        questions = get_random_questions(count)
        # Remove correct answers from response
        safe_questions = [{
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
            "category": q["category"]
        } for q in questions]
        
        logger.info(f"Quiz questions generated: {count} questions")
        return {
            "success": True,
            "questions": safe_questions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz questions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quiz questions")

@app.post("/api/quiz/submit")
@rate_limit("20/minute")
async def submit_quiz(request: Request, quiz_data: dict):
    """Submit quiz and get results"""
    try:
        answers = quiz_data.get("answers", [])
        if not answers:
            raise HTTPException(status_code=400, detail="No answers provided")
        
        # Check each answer
        results = []
        for answer in answers:
            question_id = answer.get("question_id")
            selected = answer.get("selected")
            
            if question_id is None or selected is None:
                continue
            
            result = check_answer(question_id, selected)
            if result:
                results.append({
                    "question_id": question_id,
                    "correct": result["correct"],
                    "correct_answer": result["correct_answer"],
                    "explanation": result["explanation"]
                })
        
        # Calculate score
        score = calculate_score(results)
        
        logger.info(f"Quiz submitted: {score['correct']}/{score['total']} correct")
        return {
            "success": True,
            "results": results,
            "score": score
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz submission error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit quiz")

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    uvicorn.run(app, host="0.0.0.0", port=8000)
