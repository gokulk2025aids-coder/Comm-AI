# 🚀 Multi-Language Support - Quick Start

## Get Started in 3 Minutes!

### Step 1: Start the Server (if not already running)

```bash
# Windows
start.bat

# Mac/Linux
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Step 2: Test Language Detection

Open a new terminal and run:

```bash
curl -X POST http://localhost:8000/api/detect-language ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Bonjour, comment allez-vous?\"}"
```

**Expected Output:**
```json
{
  "success": true,
  "language": {
    "code": "fr",
    "name": "French",
    "supported": true
  }
}
```

### Step 3: Try Translation

```bash
curl -X POST http://localhost:8000/api/translate ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Hello, how are you?\", \"target_lang\": \"es\"}"
```

**Expected Output:**
```json
{
  "success": true,
  "translated_text": "Hola, ¿cómo estás?",
  "target_language": "Spanish"
}
```

### Step 4: Get Cultural Tips

```bash
curl -X POST http://localhost:8000/api/cultural-tips ^
  -H "Content-Type: application/json" ^
  -d "{\"lang_code\": \"ja\"}"
```

**Expected Output:**
```json
{
  "success": true,
  "language": "Japanese",
  "tips": {
    "formality": "Very High - Extremely polite",
    "greeting": "[Name]様 (sama), お世話になっております",
    "closing": "よろしくお願いいたします, 敬具",
    "tips": "Use honorifics, be indirect, show humility, avoid direct refusals"
  }
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Analyze Foreign Email

```bash
# 1. Detect language
curl -X POST http://localhost:8000/api/detect-language ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Estimado Sr. García, Le escribo para solicitar información.\"}"

# 2. Get cultural tips for Spanish
curl -X POST http://localhost:8000/api/cultural-tips ^
  -H "Content-Type: application/json" ^
  -d "{\"lang_code\": \"es\"}"

# 3. Analyze tone with Spanish cultural context
curl -X POST http://localhost:8000/api/analyze-tone-localized ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Estimado Sr. García, Le escribo para solicitar información.\", \"lang_code\": \"es\"}"
```

### Use Case 2: Translate and Verify

```bash
# 1. Translate English to German
curl -X POST http://localhost:8000/api/translate ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Dear Sir, I kindly request your assistance.\", \"target_lang\": \"de\"}"

# 2. Check if formality is appropriate for German culture
curl -X POST http://localhost:8000/api/analyze-tone-localized ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"Sehr geehrter Herr, ich bitte höflich um Ihre Hilfe.\", \"lang_code\": \"de\"}"
```

---

## 🤖 Ask the Chatbot

Use the AI Chatbot in the web interface and ask:

- "How do I translate emails?"
- "What languages are supported?"
- "Cultural tips for Japanese emails"
- "How to write emails in German?"
- "What is localized tone analysis?"

---

## 📋 Supported Languages Cheat Sheet

| Code | Language | Formality | Key Tip |
|------|----------|-----------|---------|
| `en` | English | Medium | Direct but polite |
| `es` | Spanish | High | Warm and respectful |
| `fr` | French | High | Very formal |
| `de` | German | Very High | Direct and detailed |
| `it` | Italian | Medium-High | Warm but respectful |
| `pt` | Portuguese | Medium | Friendly and warm |
| `nl` | Dutch | Medium | Direct and practical |
| `ja` | Japanese | Very High | Extremely polite |
| `zh` | Chinese | High | Respect hierarchy |
| `ar` | Arabic | High | Very respectful |
| `hi` | Hindi | High | Respect hierarchy |
| `ru` | Russian | High | Formal in business |

---

## 🧪 Run the Test Script

```bash
python test_language_support.py
```

This will test all language features and show you examples of:
- Language detection
- Cultural tips
- Localized tone analysis
- Formality assessment

---

## 💡 Pro Tips

1. **Always detect language first** before analyzing international emails
2. **Check cultural tips** before writing to international recipients
3. **Use localized tone analysis** instead of generic analysis for better cultural insights
4. **Verify formality levels** match the expected culture (e.g., Japanese expects 8/10)
5. **Review translations** - automatic translation is good but not perfect for business-critical emails

---

## 🔗 More Information

- **Full Guide:** See `LANGUAGE_SUPPORT.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Main Documentation:** See `README.md`

---

## ✅ Quick Verification

Run these commands to verify everything works:

```bash
# Test 1: Language Detection
curl -X POST http://localhost:8000/api/detect-language -H "Content-Type: application/json" -d "{\"text\": \"Hello\"}"

# Test 2: Translation
curl -X POST http://localhost:8000/api/translate -H "Content-Type: application/json" -d "{\"text\": \"Hello\", \"target_lang\": \"es\"}"

# Test 3: Cultural Tips
curl -X POST http://localhost:8000/api/cultural-tips -H "Content-Type: application/json" -d "{\"lang_code\": \"en\"}"

# Test 4: Localized Analysis
curl -X POST http://localhost:8000/api/analyze-tone-localized -H "Content-Type: application/json" -d "{\"text\": \"Hello\", \"lang_code\": \"en\"}"
```

If all 4 tests return `"success": true`, you're ready to go! 🎉

---

**Need Help?** Check the logs in `commai.log` or review the full documentation.
