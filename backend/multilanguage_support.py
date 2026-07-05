from textblob import TextBlob
from deep_translator import GoogleTranslator
from langdetect import detect, detect_langs
import re

class MultiLanguageSupport:
    def __init__(self):
        pass
        
        # Supported languages
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'pl': 'Polish',
            'tr': 'Turkish',
            'vi': 'Vietnamese',
            'th': 'Thai',
            'id': 'Indonesian'
        }
        
        # Cultural communication tips
        self.cultural_tips = {
            'en': {
                'formality': 'Medium - Balance between formal and casual',
                'greeting': 'Hi/Hello for casual, Dear for formal',
                'closing': 'Best regards, Sincerely, Thanks',
                'directness': 'Direct communication is appreciated',
                'tips': [
                    'Be clear and concise',
                    'Use active voice',
                    'Get to the point quickly',
                    'Professional but friendly tone is common',
                    'Use bullet points for clarity'
                ]
            },
            'es': {
                'formality': 'High - More formal than English',
                'greeting': 'Estimado/a (formal), Hola (casual)',
                'closing': 'Atentamente, Cordialmente, Saludos',
                'directness': 'Slightly indirect, polite phrasing preferred',
                'tips': [
                    'Use formal "usted" for business',
                    'Include warm greetings and closings',
                    'Build rapport before business',
                    'Show respect with formal titles',
                    'Longer emails are acceptable'
                ]
            },
            'fr': {
                'formality': 'Very High - Formal language expected',
                'greeting': 'Madame/Monsieur (formal), Bonjour (casual)',
                'closing': 'Cordialement, Bien cordialement',
                'directness': 'Indirect, diplomatic language preferred',
                'tips': [
                    'Always use "vous" in business',
                    'Maintain formal structure',
                    'Avoid being too direct',
                    'Use proper titles and honorifics',
                    'Quality of language matters'
                ]
            },
            'de': {
                'formality': 'High - Formal and structured',
                'greeting': 'Sehr geehrte/r (formal), Hallo (casual)',
                'closing': 'Mit freundlichen Grüßen, Beste Grüße',
                'directness': 'Direct and clear communication valued',
                'tips': [
                    'Use "Sie" for formal communication',
                    'Be precise and detailed',
                    'Structure is important',
                    'Punctuality references appreciated',
                    'Professional titles matter'
                ]
            },
            'ja': {
                'formality': 'Very High - Extremely formal',
                'greeting': 'お世話になっております (standard business)',
                'closing': 'よろしくお願いいたします',
                'directness': 'Very indirect, harmony-focused',
                'tips': [
                    'Use keigo (honorific language)',
                    'Avoid direct refusals',
                    'Show humility and respect',
                    'Context is more important than words',
                    'Apologize frequently as courtesy'
                ]
            },
            'zh-cn': {
                'formality': 'High - Respect hierarchy',
                'greeting': '尊敬的 (formal), 你好 (casual)',
                'closing': '此致敬礼, 祝好',
                'directness': 'Indirect, face-saving important',
                'tips': [
                    'Show respect for hierarchy',
                    'Build relationships first',
                    'Avoid causing embarrassment',
                    'Use appropriate titles',
                    'Group harmony over individual'
                ]
            },
            'ar': {
                'formality': 'Very High - Formal and respectful',
                'greeting': 'السلام عليكم (Peace be upon you)',
                'closing': 'مع أطيب التحيات (With best regards)',
                'directness': 'Indirect, elaborate language valued',
                'tips': [
                    'Use elaborate greetings',
                    'Show respect and hospitality',
                    'Avoid being too direct',
                    'Religious references acceptable',
                    'Relationship-focused communication'
                ]
            },
            'pt': {
                'formality': 'Medium-High - Warm but professional',
                'greeting': 'Prezado/a (formal), Olá (casual)',
                'closing': 'Atenciosamente, Cordialmente',
                'directness': 'Moderately indirect, friendly',
                'tips': [
                    'Be warm and personable',
                    'Build rapport before business',
                    'Use formal "você" or "senhor/a"',
                    'Emotional expression acceptable',
                    'Relationship matters'
                ]
            },
            'ru': {
                'formality': 'High - Formal in business',
                'greeting': 'Уважаемый/ая (formal), Здравствуйте',
                'closing': 'С уважением, С наилучшими пожеланиями',
                'directness': 'Direct but formal',
                'tips': [
                    'Use formal "Вы" in business',
                    'Be direct but respectful',
                    'Detailed explanations valued',
                    'Show competence and expertise',
                    'Formal titles important'
                ]
            },
            'ko': {
                'formality': 'Very High - Hierarchical',
                'greeting': '안녕하십니까 (formal)',
                'closing': '감사합니다 (Thank you)',
                'directness': 'Indirect, respect-focused',
                'tips': [
                    'Use honorific language (존댓말)',
                    'Respect age and position',
                    'Avoid direct confrontation',
                    'Show humility',
                    'Hierarchy is crucial'
                ]
            }
        }
    
    def detect_language(self, text):
        """Detect the language of the text"""
        try:
            lang_code = detect(text)
            lang_name = self.supported_languages.get(lang_code, 'Unknown')
            
            # Get confidence
            try:
                langs = detect_langs(text)
                confidence = langs[0].prob * 100 if langs else 0
            except:
                confidence = 0
            
            return {
                'language_code': lang_code,
                'language_name': lang_name,
                'confidence': round(confidence, 1),
                'supported': lang_code in self.supported_languages
            }
        except Exception as e:
            return {
                'language_code': 'unknown',
                'language_name': 'Unknown',
                'confidence': 0,
                'supported': False,
                'error': str(e)
            }
    
    def translate_text(self, text, target_lang='en', source_lang='auto'):
        """Translate text to target language"""
        try:
            # Detect source language if auto
            if source_lang == 'auto':
                detected = self.detect_language(text)
                source_lang = detected['language_code']
            
            # Translate using deep-translator
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            
            return {
                'success': True,
                'original_text': text,
                'translated_text': translated,
                'source_language': source_lang,
                'target_language': target_lang,
                'source_language_name': self.supported_languages.get(source_lang, 'Unknown'),
                'target_language_name': self.supported_languages.get(target_lang, 'Unknown')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Translation failed. Please check the text and language codes.'
            }
    
    def get_cultural_tips(self, language_code):
        """Get cultural communication tips for a language"""
        if language_code not in self.cultural_tips:
            return {
                'language': self.supported_languages.get(language_code, 'Unknown'),
                'available': False,
                'message': 'Cultural tips not available for this language yet.'
            }
        
        tips = self.cultural_tips[language_code]
        return {
            'language': self.supported_languages.get(language_code, 'Unknown'),
            'language_code': language_code,
            'available': True,
            'formality_level': tips['formality'],
            'greeting_style': tips['greeting'],
            'closing_style': tips['closing'],
            'directness': tips['directness'],
            'communication_tips': tips['tips']
        }
    
    def analyze_multilingual_email(self, text):
        """Comprehensive multilingual email analysis"""
        # Detect language
        detection = self.detect_language(text)
        
        if not detection['supported']:
            return {
                'error': 'Language not supported or could not be detected',
                'detected_language': detection['language_name']
            }
        
        lang_code = detection['language_code']
        
        # Get cultural tips
        cultural_tips = self.get_cultural_tips(lang_code)
        
        # Analyze tone (localized)
        tone_analysis = self._analyze_localized_tone(text, lang_code)
        
        # Translate to English for universal understanding
        translation = None
        if lang_code != 'en':
            translation = self.translate_text(text, target_lang='en', source_lang=lang_code)
        
        return {
            'success': True,
            'language_detection': detection,
            'cultural_tips': cultural_tips,
            'tone_analysis': tone_analysis,
            'translation_to_english': translation,
            'recommendations': self._generate_localized_recommendations(text, lang_code, tone_analysis)
        }
    
    def _analyze_localized_tone(self, text, lang_code):
        """Analyze tone considering cultural context"""
        # Basic sentiment analysis
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
        except:
            polarity = 0
        
        # Formality indicators by language
        formality_indicators = {
            'en': ['dear', 'sincerely', 'respectfully', 'kindly', 'please'],
            'es': ['estimado', 'atentamente', 'cordialmente', 'usted'],
            'fr': ['madame', 'monsieur', 'cordialement', 'vous'],
            'de': ['sehr geehrte', 'mit freundlichen grüßen', 'sie'],
            'ja': ['お世話になっております', 'よろしくお願い', 'ございます'],
            'zh-cn': ['尊敬', '您', '敬礼'],
            'ar': ['السلام عليكم', 'حضرة'],
            'pt': ['prezado', 'atenciosamente', 'senhor'],
            'ru': ['уважаемый', 'с уважением', 'вы'],
            'ko': ['안녕하십니까', '감사합니다', '님']
        }
        
        text_lower = text.lower()
        formal_words = formality_indicators.get(lang_code, [])
        formality_count = sum(1 for word in formal_words if word in text_lower)
        
        # Determine formality
        if formality_count >= 2:
            formality = 'Formal'
        elif formality_count == 1:
            formality = 'Semi-formal'
        else:
            formality = 'Casual'
        
        # Determine sentiment
        if polarity > 0.2:
            sentiment = 'Positive'
        elif polarity < -0.2:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return {
            'formality': formality,
            'sentiment': sentiment,
            'polarity': round(polarity, 2),
            'culturally_appropriate': self._check_cultural_appropriateness(formality, lang_code)
        }
    
    def _check_cultural_appropriateness(self, formality, lang_code):
        """Check if formality level is appropriate for the culture"""
        # Expected formality by language
        expected_formality = {
            'en': 'Semi-formal',
            'es': 'Formal',
            'fr': 'Formal',
            'de': 'Formal',
            'ja': 'Formal',
            'zh-cn': 'Formal',
            'ar': 'Formal',
            'pt': 'Semi-formal',
            'ru': 'Formal',
            'ko': 'Formal'
        }
        
        expected = expected_formality.get(lang_code, 'Semi-formal')
        
        if formality == expected:
            return {
                'appropriate': True,
                'message': f'Formality level is appropriate for {self.supported_languages.get(lang_code)} business communication'
            }
        elif formality == 'Casual' and expected == 'Formal':
            return {
                'appropriate': False,
                'message': f'Too casual for {self.supported_languages.get(lang_code)} business culture. Consider using more formal language.'
            }
        else:
            return {
                'appropriate': True,
                'message': 'Formality level is acceptable'
            }
    
    def _generate_localized_recommendations(self, text, lang_code, tone_analysis):
        """Generate recommendations based on language and culture"""
        recommendations = []
        
        # Check formality
        if not tone_analysis['culturally_appropriate']['appropriate']:
            recommendations.append({
                'type': 'warning',
                'category': 'Cultural Appropriateness',
                'message': tone_analysis['culturally_appropriate']['message']
            })
        
        # Check length (some cultures prefer longer emails)
        word_count = len(text.split())
        if lang_code in ['ja', 'zh-cn', 'ar', 'ko'] and word_count < 30:
            recommendations.append({
                'type': 'info',
                'category': 'Length',
                'message': f'In {self.supported_languages.get(lang_code)} culture, slightly longer emails with proper greetings are preferred.'
            })
        
        # Check directness
        if lang_code in ['ja', 'zh-cn', 'ko'] and any(word in text.lower() for word in ['no', 'cannot', 'impossible', 'refuse']):
            recommendations.append({
                'type': 'warning',
                'category': 'Directness',
                'message': f'{self.supported_languages.get(lang_code)} culture values indirect communication. Consider softening direct refusals.'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'category': 'Overall',
                'message': 'Email appears culturally appropriate!'
            })
        
        return recommendations
    
    def get_supported_languages(self):
        """Get list of all supported languages"""
        return [
            {'code': code, 'name': name}
            for code, name in self.supported_languages.items()
        ]
