from textblob import TextBlob
import re
import logging
from deep_translator import GoogleTranslator
from langdetect import detect, detect_langs

logger = logging.getLogger(__name__)

logger.info("Language support loaded with deep-translator")

class LanguageSupport:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'nl': 'Dutch',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'zh-cn': 'Chinese',
            'zh-tw': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'ru': 'Russian',
            'ta': 'Tamil',
            'ko': 'Korean'
        }
        
        self.cultural_tips = {
            'en': {
                'formality': 'Medium - Direct but polite',
                'greeting': 'Hi/Hello [Name] or Dear [Name]',
                'closing': 'Best regards, Sincerely, Thanks',
                'tips': 'Be concise, get to the point quickly, use active voice'
            },
            'es': {
                'formality': 'High - Respectful and warm',
                'greeting': 'Estimado/a [Name] (formal), Hola [Name] (casual)',
                'closing': 'Atentamente, Cordialmente, Saludos',
                'tips': 'Show warmth, build rapport, use formal usted for business'
            },
            'fr': {
                'formality': 'High - Very formal in business',
                'greeting': 'Madame/Monsieur [Name], Bonjour [Name]',
                'closing': 'Cordialement, Bien à vous, Salutations',
                'tips': 'Use formal vous, maintain professional distance, be polite'
            },
            'de': {
                'formality': 'Very High - Extremely formal',
                'greeting': 'Sehr geehrte/r [Name], Guten Tag [Name]',
                'closing': 'Mit freundlichen Grüßen, Hochachtungsvoll',
                'tips': 'Be direct, detailed, punctual, use Sie for formal communication'
            },
            'it': {
                'formality': 'Medium-High - Warm but respectful',
                'greeting': 'Gentile [Name], Caro/a [Name]',
                'closing': 'Cordiali saluti, Distinti saluti',
                'tips': 'Show enthusiasm, build relationships, use Lei for formal'
            },
            'pt': {
                'formality': 'Medium - Friendly and warm',
                'greeting': 'Prezado/a [Name], Olá [Name]',
                'closing': 'Atenciosamente, Cordialmente, Abraços',
                'tips': 'Be warm, personal, relationship-focused, flexible with time'
            },
            'ja': {
                'formality': 'Very High - Extremely polite',
                'greeting': '[Name]様 (sama), お世話になっております',
                'closing': 'よろしくお願いいたします, 敬具',
                'tips': 'Use honorifics, be indirect, show humility, avoid direct refusals'
            },
            'zh': {
                'formality': 'High - Respectful hierarchy',
                'greeting': '尊敬的[Name], 您好',
                'closing': '此致敬礼, 祝好',
                'tips': 'Respect hierarchy, build relationships, be patient, save face'
            },
            'ar': {
                'formality': 'High - Very respectful',
                'greeting': 'السيد/ة [Name], تحية طيبة',
                'closing': 'مع خالص التحية, تفضلوا بقبول فائق الاحترام',
                'tips': 'Show respect, build trust, be patient, relationship-first'
            },
            'hi': {
                'formality': 'High - Respectful with hierarchy',
                'greeting': 'आदरणीय [Name], नमस्ते',
                'closing': 'धन्यवाद, सादर',
                'tips': 'Respect hierarchy, use titles, build relationships, be formal'
            },
            'ru': {
                'formality': 'High - Formal in business',
                'greeting': 'Уважаемый/ая [Name], Здравствуйте',
                'closing': 'С уважением, Всего доброго',
                'tips': 'Be formal, direct, detailed, use вы for formal communication'
            },
            'nl': {
                'formality': 'Medium - Direct and practical',
                'greeting': 'Geachte [Name], Beste [Name]',
                'closing': 'Met vriendelijke groet, Hoogachtend',
                'tips': 'Be direct, practical, egalitarian, use u for formal'
            },
            'ta': {
                'formality': 'High - Respectful with hierarchy',
                'greeting': 'மதிப்பிற்குரிய [Name], வணக்கம்',
                'closing': 'நன்றி, வணக்கத்துடன்',
                'tips': 'Show respect for elders and hierarchy, use honorifics, be polite and formal in business, relationship-focused communication'
            }
        }
    
    def detect_language(self, text):
        """Detect language of text"""
        try:
            # Use langdetect for better accuracy
            lang_code = detect(text)
            
            # Get confidence
            try:
                langs = detect_langs(text)
                confidence = langs[0].prob if langs else 0.9
            except:
                confidence = 0.9
            
            return {
                'code': lang_code,
                'name': self.supported_languages.get(lang_code, 'Unknown'),
                'supported': lang_code in self.supported_languages,
                'confidence': round(confidence * 100, 1)
            }
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return {'code': 'en', 'name': 'English', 'supported': True, 'confidence': 0}
    
    def translate_text(self, text, target_lang='en'):
        """Translate text to target language with improved accuracy"""
        try:
            # Detect source language
            detected = detect(text)
            source_lang = detected
            
            # Map language codes for deep-translator compatibility
            lang_map = {
                'zh-cn': 'zh-CN',
                'zh-tw': 'zh-TW',
                'zh': 'zh-CN'
            }
            
            # Convert source and target to proper format
            source_lang = lang_map.get(source_lang, source_lang)
            target_lang = lang_map.get(target_lang, target_lang)
            
            logger.info(f"Translating from {source_lang} to {target_lang} using deep-translator")
            
            # If source and target are the same, return original
            if source_lang.lower() == target_lang.lower():
                return text
            
            # Translate using deep-translator with auto-detect
            translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
            
            # Verify translation is not empty
            if not translated_text or translated_text.strip() == '':
                logger.error("Translation returned empty string")
                raise Exception("Empty translation result")
            
            logger.info(f"Translation successful: {len(translated_text)} characters")
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation failed: {type(e).__name__} - {str(e)}")
            logger.error(f"Full error details: {e}")
            
            # Try one more time with simplified approach
            try:
                logger.info("Attempting fallback translation...")
                translated_text = GoogleTranslator(source='auto', target='en').translate(text)
                if translated_text and translated_text.strip():
                    logger.info("Fallback translation successful")
                    return translated_text
            except Exception as fallback_error:
                logger.error(f"Fallback translation also failed: {fallback_error}")
            
            # Provide helpful error message
            error_msg = "⚠️ Translation Service Unavailable\n\n"
            error_msg += "We're having trouble connecting to the translation service. "
            error_msg += "This usually happens when:\n\n"
            error_msg += "• Internet connection is slow or unstable\n"
            error_msg += "• Translation service is temporarily down\n"
            error_msg += "• The text contains unsupported characters\n\n"
            error_msg += "💡 What you can do:\n"
            error_msg += "1. Check your internet connection\n"
            error_msg += "2. Try translating a shorter text first\n"
            error_msg += "3. Wait a moment and try again\n"
            error_msg += "4. Use Google Translate website directly: translate.google.com\n\n"
            error_msg += f"Original text: {text[:200]}{'...' if len(text) > 200 else ''}"
            
            return error_msg
    
    def get_cultural_tips(self, lang_code):
        """Get cultural communication tips for language"""
        return self.cultural_tips.get(lang_code, self.cultural_tips['en'])
    
    def analyze_tone_localized(self, text, lang_code):
        """Analyze tone with cultural context"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        # Base tone detection
        if polarity > 0.3:
            base_tone = "Positive"
        elif polarity < -0.3:
            base_tone = "Negative"
        else:
            base_tone = "Neutral"
        
        # Cultural adjustments
        cultural_context = ""
        if lang_code == 'ja':
            cultural_context = "Japanese communication values indirectness and politeness. Even neutral messages should include honorifics."
        elif lang_code == 'de':
            cultural_context = "German communication values directness and clarity. Formal tone is expected in business."
        elif lang_code == 'es' or lang_code == 'pt':
            cultural_context = "Spanish/Portuguese communication values warmth and personal connection. Add friendly elements."
        elif lang_code == 'ar' or lang_code == 'hi':
            cultural_context = "Arabic/Hindi communication values respect and hierarchy. Use formal titles and respectful language."
        elif lang_code == 'zh':
            cultural_context = "Chinese communication values harmony and face-saving. Avoid direct confrontation."
        elif lang_code == 'fr':
            cultural_context = "French communication values formality and eloquence. Maintain professional distance."
        elif lang_code == 'ta':
            cultural_context = "Tamil communication values respect for elders and hierarchy. Use honorifics and maintain formal tone in business."
        else:
            cultural_context = "English communication values clarity and efficiency. Be direct but polite."
        
        return {
            'tone': base_tone,
            'polarity': round(polarity, 2),
            'cultural_context': cultural_context,
            'tips': self.cultural_tips.get(lang_code, self.cultural_tips['en'])
        }
    
    def get_formality_level(self, text, lang_code):
        """Assess formality level with cultural context"""
        formal_indicators = ['please', 'kindly', 'regards', 'sincerely', 'respectfully']
        text_lower = text.lower()
        
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
        
        # Cultural baseline adjustments
        baseline = {
            'ja': 8, 'de': 7, 'ar': 7, 'hi': 7, 'zh': 7, 'ta': 7,
            'fr': 6, 'ru': 6,
            'es': 5, 'it': 5, 'pt': 5,
            'en': 5, 'nl': 4
        }
        
        base_score = baseline.get(lang_code, 5)
        score = min(10, base_score + formal_count)
        
        if score >= 8:
            level = "Very Formal"
        elif score >= 6:
            level = "Formal"
        elif score >= 4:
            level = "Neutral"
        else:
            level = "Casual"
        
        return {
            'level': level,
            'score': score,
            'expected_for_culture': f"Expected formality for {self.supported_languages.get(lang_code, 'this language')}: {base_score}/10"
        }
