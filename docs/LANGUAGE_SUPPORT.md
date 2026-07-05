# 🌐 Multi-Language Support - Usage Guide

## Overview

CommAI now supports comprehensive multi-language email analysis with translation, cultural tips, and localized tone analysis for 12+ languages.

---

## Supported Languages

| Code | Language | Cultural Context |
|------|----------|------------------|
| `en` | English | Direct, efficient, medium formality |
| `es` | Spanish | Warm, respectful, high formality |
| `fr` | French | Very formal, eloquent, professional distance |
| `de` | German | Extremely formal, direct, detailed |
| `it` | Italian | Warm but respectful, medium-high formality |
| `pt` | Portuguese | Friendly, warm, relationship-focused |
| `nl` | Dutch | Direct, practical, medium formality |
| `ja` | Japanese | Extremely polite, indirect, very high formality |
| `zh` | Chinese | Respectful hierarchy, high formality |
| `ar` | Arabic | Very respectful, relationship-first |
| `hi` | Hindi | Respectful hierarchy, high formality |
| `ru` | Russian | Formal in business, direct, detailed |

---

## API Endpoints

### 1. Detect Language

**Endpoint:** `POST /api/detect-language`

**Request:**
```json
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

---

### 2. Translate Email

**Endpoint:** `POST /api/translate`

**Request:**
```json
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

**Supported target languages:** `en`, `es`, `fr`, `de`, `it`, `pt`, `nl`, `ja`, `zh`, `ar`, `hi`, `ru`

---

### 3. Get Cultural Tips

**Endpoint:** `POST /api/cultural-tips`

**Request:**
```json
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
    "tips": "Use honorifics, be indirect, show humility, avoid direct refusals"
  }
}
```

---

### 4. Analyze Tone (Localized)

**Endpoint:** `POST /api/analyze-tone-localized`

**Request:**
```json
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
    "cultural_context": "German communication values directness and clarity. Formal tone is expected in business.",
    "tips": {
      "formality": "Very High - Extremely formal",
      "greeting": "Sehr geehrte/r [Name], Guten Tag [Name]",
      "closing": "Mit freundlichen Grüßen, Hochachtungsvoll",
      "tips": "Be direct, detailed, punctual, use Sie for formal communication"
    }
  },
  "formality": {
    "level": "Formal",
    "score": 7,
    "expected_for_culture": "Expected formality for German: 7/10"
  }
}
```

---

## Usage Examples

### Example 1: Analyze Spanish Email

```python
import requests

# Detect language
response = requests.post('http://localhost:8000/api/detect-language', json={
    'text': 'Estimado Sr. García, Le escribo para solicitar información.'
})
print(response.json())
# Output: {"language": {"code": "es", "name": "Spanish", "supported": true}}

# Get cultural tips
response = requests.post('http://localhost:8000/api/cultural-tips', json={
    'lang_code': 'es'
})
print(response.json()['tips'])
```

### Example 2: Translate and Analyze

```python
# Translate from English to Japanese
response = requests.post('http://localhost:8000/api/translate', json={
    'text': 'Thank you for your assistance.',
    'target_lang': 'ja'
})
translated = response.json()['translated_text']

# Analyze with Japanese cultural context
response = requests.post('http://localhost:8000/api/analyze-tone-localized', json={
    'text': translated,
    'lang_code': 'ja'
})
print(response.json())
```

### Example 3: Check Formality for Different Cultures

```python
email_text = "Dear Sir, I kindly request your assistance. Best regards."

for lang in ['en', 'ja', 'de', 'pt']:
    response = requests.post('http://localhost:8000/api/analyze-tone-localized', json={
        'text': email_text,
        'lang_code': lang
    })
    formality = response.json()['formality']
    print(f"{lang}: {formality['level']} ({formality['score']}/10)")
```

---

## Chatbot Integration

The AI chatbot now understands multi-language queries:

**Ask about translation:**
- "How do I translate emails?"
- "What languages are supported?"

**Ask about cultural tips:**
- "How to write emails in Japanese?"
- "What's the communication style in Germany?"
- "Cultural tips for Spanish emails"

**Ask about localized analysis:**
- "What is localized tone analysis?"
- "How does formality differ by culture?"

---

## Best Practices

### 1. Always Detect Language First
Before analyzing or translating, detect the language to ensure proper handling.

### 2. Use Cultural Tips
Review cultural communication tips before writing emails to international recipients.

### 3. Check Formality Levels
Different cultures expect different formality levels. Use the formality assessment to match expectations.

### 4. Localized Tone Analysis
Use localized tone analysis instead of generic analysis for international emails to get culturally appropriate feedback.

### 5. Translation Quality
While translation is automatic, always review translated text for accuracy, especially for business-critical communications.

---

## Cultural Communication Quick Reference

### High Formality Cultures (Score 7-8/10)
- **Japanese, German, Arabic, Hindi, Chinese**
- Use formal titles, honorifics, and respectful language
- Avoid casual expressions
- Be patient with decision-making

### Medium Formality Cultures (Score 5-6/10)
- **English, French, Spanish, Italian, Russian**
- Balance professionalism with approachability
- Use appropriate greetings and closings
- Match recipient's tone

### Lower Formality Cultures (Score 4-5/10)
- **Portuguese, Dutch**
- More casual but still professional
- Build personal relationships
- Be warm and friendly

---

## Error Handling

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

Common errors:
- `400`: Invalid request (missing fields, invalid language code)
- `500`: Server error (translation failed, detection error)

---

## Rate Limits

- Language Detection: 30 requests/minute
- Translation: 20 requests/minute
- Cultural Tips: 30 requests/minute
- Localized Tone Analysis: 30 requests/minute

---

## Testing

Run the test script to verify functionality:

```bash
python test_language_support.py
```

This will test:
- Language detection
- Cultural tips retrieval
- Localized tone analysis
- Formality assessment

---

## Future Enhancements

Planned features:
- Real-time translation in UI
- Language-specific templates
- Cultural sensitivity scoring
- Multi-language PDF reports
- Voice tone analysis per culture

---

**Built with ❤️ for global communication**
