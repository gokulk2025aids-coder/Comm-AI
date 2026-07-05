# 🏗️ Multi-Language Support - System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CommAI Application                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (main.py)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                           │  │
│  │  • POST /api/detect-language                             │  │
│  │  • POST /api/translate                                   │  │
│  │  • POST /api/cultural-tips                               │  │
│  │  • POST /api/analyze-tone-localized                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              Language Support Module (language_support.py)       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Core Functions:                                          │  │
│  │  • detect_language(text) → language info                 │  │
│  │  • translate_text(text, target_lang) → translated text   │  │
│  │  • get_cultural_tips(lang_code) → cultural guidelines    │  │
│  │  • analyze_tone_localized(text, lang) → tone + context   │  │
│  │  • get_formality_level(text, lang) → formality score     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TextBlob NLP Library                          │
│  • Language Detection                                            │
│  • Translation Engine                                            │
│  • Sentiment Analysis                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. Language Detection Flow

```
User Email Text
      │
      ▼
┌─────────────────┐
│ Detect Language │
│   Endpoint      │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│   TextBlob      │
│   Detection     │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  Return Result  │
│  • code: "es"   │
│  • name: "Spanish"│
│  • supported: true│
└─────────────────┘
```

### 2. Translation Flow

```
Source Text + Target Language
      │
      ▼
┌─────────────────┐
│   Translate     │
│   Endpoint      │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│   TextBlob      │
│   Translation   │
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Translated Text │
└─────────────────┘
```

### 3. Cultural Analysis Flow

```
Email Text + Language Code
      │
      ├─────────────────┐
      ▼                 ▼
┌──────────┐    ┌──────────────┐
│ Cultural │    │   Localized  │
│   Tips   │    │ Tone Analysis│
└──────────┘    └──────────────┘
      │                 │
      ▼                 ▼
┌──────────┐    ┌──────────────┐
│ Formality│    │   Sentiment  │
│  Rules   │    │   Analysis   │
└──────────┘    └──────────────┘
      │                 │
      └────────┬────────┘
               ▼
    ┌──────────────────┐
    │ Combined Results │
    │ • Tone           │
    │ • Cultural Tips  │
    │ • Formality      │
    │ • Context        │
    └──────────────────┘
```

---

## Component Interaction

```
┌──────────────┐
│   Frontend   │
│  (Optional)  │
└──────┬───────┘
       │ HTTP Request
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   FastAPI    │────▶│   Language   │────▶│   TextBlob   │
│   Endpoints  │     │   Support    │     │   Library    │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       │ JSON Response
       ▼
┌──────────────┐
│     User     │
└──────────────┘
```

---

## Language Support Module Structure

```
LanguageSupport Class
│
├── __init__()
│   ├── supported_languages (dict)
│   │   └── 12 language codes → names
│   │
│   └── cultural_tips (dict)
│       └── 12 languages → cultural guidelines
│
├── detect_language(text)
│   └── Returns: {code, name, supported}
│
├── translate_text(text, target_lang)
│   └── Returns: translated string
│
├── get_cultural_tips(lang_code)
│   └── Returns: {formality, greeting, closing, tips}
│
├── analyze_tone_localized(text, lang_code)
│   └── Returns: {tone, polarity, cultural_context, tips}
│
└── get_formality_level(text, lang_code)
    └── Returns: {level, score, expected_for_culture}
```

---

## Cultural Tips Data Structure

```
cultural_tips = {
    'en': {
        'formality': 'Medium - Direct but polite',
        'greeting': 'Hi/Hello [Name] or Dear [Name]',
        'closing': 'Best regards, Sincerely, Thanks',
        'tips': 'Be concise, get to the point quickly...'
    },
    'ja': {
        'formality': 'Very High - Extremely polite',
        'greeting': '[Name]様 (sama), お世話になっております',
        'closing': 'よろしくお願いいたします, 敬具',
        'tips': 'Use honorifics, be indirect...'
    },
    // ... 10 more languages
}
```

---

## API Request/Response Examples

### Detect Language

**Request:**
```json
POST /api/detect-language
{
  "text": "Bonjour, comment allez-vous?"
}
```

**Response:**
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

### Translate

**Request:**
```json
POST /api/translate
{
  "text": "Hello, how are you?",
  "target_lang": "es"
}
```

**Response:**
```json
{
  "success": true,
  "translated_text": "Hola, ¿cómo estás?",
  "target_language": "Spanish"
}
```

### Cultural Tips

**Request:**
```json
POST /api/cultural-tips
{
  "lang_code": "ja"
}
```

**Response:**
```json
{
  "success": true,
  "language": "Japanese",
  "tips": {
    "formality": "Very High - Extremely polite",
    "greeting": "[Name]様 (sama), お世話になっております",
    "closing": "よろしくお願いいたします, 敬具",
    "tips": "Use honorifics, be indirect, show humility..."
  }
}
```

### Localized Tone Analysis

**Request:**
```json
POST /api/analyze-tone-localized
{
  "text": "Dear Sir, I kindly request your assistance.",
  "lang_code": "de"
}
```

**Response:**
```json
{
  "success": true,
  "tone_analysis": {
    "tone": "Neutral",
    "polarity": 0.15,
    "cultural_context": "German communication values directness...",
    "tips": { /* cultural tips */ }
  },
  "formality": {
    "level": "Formal",
    "score": 7,
    "expected_for_culture": "Expected formality for German: 7/10"
  }
}
```

---

## Integration Points

### 1. With Email Analyzer
```
Email Text → Language Detection → Localized Analysis → Results
```

### 2. With Chatbot
```
User Query → Language Support Knowledge → Chatbot Response
```

### 3. With PDF Generator (Future)
```
Analysis Results → Language-Specific Formatting → PDF Report
```

---

## Formality Scoring System

```
Formality Baseline by Culture:
┌────────────┬───────┬──────────────────┐
│ Language   │ Score │ Description      │
├────────────┼───────┼──────────────────┤
│ Japanese   │  8/10 │ Very High        │
│ German     │  7/10 │ Very High        │
│ Arabic     │  7/10 │ Very High        │
│ Hindi      │  7/10 │ Very High        │
│ Chinese    │  7/10 │ High             │
│ French     │  6/10 │ High             │
│ Russian    │  6/10 │ High             │
│ Spanish    │  5/10 │ Medium-High      │
│ Italian    │  5/10 │ Medium-High      │
│ Portuguese │  5/10 │ Medium           │
│ English    │  5/10 │ Medium           │
│ Dutch      │  4/10 │ Medium-Low       │
└────────────┴───────┴──────────────────┘

Adjustments:
+ Formal words (please, kindly, regards) → +1 each
+ Proper structure (greeting, closing) → +1
- Casual language → -1
- Missing structure → -1
```

---

## Error Handling Flow

```
API Request
    │
    ▼
┌─────────────┐
│ Validation  │
│  - Text?    │
│  - Lang?    │
└─────┬───────┘
      │
      ├─ Valid ──────────────┐
      │                      ▼
      │              ┌──────────────┐
      │              │   Process    │
      │              │   Request    │
      │              └──────┬───────┘
      │                     │
      │                     ├─ Success ──▶ Return Result
      │                     │
      │                     └─ Error ────▶ Log & Fallback
      │
      └─ Invalid ──▶ Return 400 Error
```

---

## Performance Considerations

### Caching Strategy (Future Enhancement)
```
┌──────────────────┐
│ Language Cache   │
│ • Detected langs │
│ • Translations   │
│ • Cultural tips  │
└──────────────────┘
```

### Rate Limiting
```
Endpoint                    Limit
─────────────────────────────────
/api/detect-language        30/min
/api/translate              20/min
/api/cultural-tips          30/min
/api/analyze-tone-localized 30/min
```

---

## Testing Architecture

```
test_language_support.py
│
├── Test 1: Language Detection
│   └── Verify 4 languages detected correctly
│
├── Test 2: Cultural Tips
│   └── Verify tips for 4 languages
│
├── Test 3: Localized Tone Analysis
│   └── Verify cultural context for 3 languages
│
└── Test 4: Formality Assessment
    └── Verify scores for 4 cultures
```

---

## Future Architecture Enhancements

```
┌─────────────────────────────────────────┐
│         Future Enhancements             │
├─────────────────────────────────────────┤
│ • Real-time UI translation              │
│ • Language-specific templates           │
│ • Multi-language PDF reports            │
│ • Batch translation                     │
│ • User language preferences             │
│ • Cultural sensitivity scoring          │
│ • Voice tone analysis per culture       │
└─────────────────────────────────────────┘
```

---

## Security & Privacy

```
┌──────────────────────────────────────┐
│ Security Measures                    │
├──────────────────────────────────────┤
│ ✓ Input validation (length, format) │
│ ✓ Rate limiting per endpoint         │
│ ✓ Error logging (no sensitive data) │
│ ✓ SQL injection prevention           │
│ ✓ No data storage (stateless)       │
└──────────────────────────────────────┘
```

---

**This architecture provides a scalable, maintainable foundation for multi-language email analysis.**
