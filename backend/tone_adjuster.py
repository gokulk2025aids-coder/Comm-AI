import re
from textblob import TextBlob

class ToneAdjuster:
    def __init__(self):
        self.casual_formal_map = {
            r'\bhey\b': 'Dear',
            r'\bhi\b': 'Hello',
            r'\byeah\b': 'yes',
            r'\bnope\b': 'no',
            r'\bgonna\b': 'going to',
            r'\bwanna\b': 'want to',
            r'\bgotta\b': 'have to',
            r'\bkinda\b': 'somewhat',
            r'\bsorta\b': 'somewhat',
            r'\bthanks\b': 'Thank you',
            r'\bbye\b': 'Best regards',
            r'\bok\b': 'acceptable',
            r'\bokay\b': 'acceptable',
            r'\bguys\b': 'everyone',
            r'\bstuff\b': 'matters',
            r'\bthing\b': 'matter',
            r'\banyway\b': 'nevertheless',
            r'\bbasically\b': 'essentially',
            r'\bpretty\b': 'quite',
            r'\breally\b': 'very',
            r"\bcan't\b": 'cannot',
            r"\bwon't\b": 'will not',
            r"\bdon't\b": 'do not',
            r"\bdidn't\b": 'did not',
            r"\bisn't\b": 'is not',
            r"\baren't\b": 'are not',
            r"\bwasn't\b": 'was not',
            r"\bweren't\b": 'were not',
        }
        
        self.aggressive_diplomatic_map = {
            r'\byou must\b': 'I would appreciate if you could',
            r'\byou need to\b': 'it would be helpful if you could',
            r'\byou should\b': 'I suggest',
            r'\bimmediately\b': 'at your earliest convenience',
            r'\bwrong\b': 'may need reconsideration',
            r'\bbad\b': 'could be improved',
            r'\bterrible\b': 'needs improvement',
            r'\bunacceptable\b': 'not meeting expectations',
            r'\bdemand\b': 'request',
            r'\bfix this\b': 'please address this',
            r'\bnever\b': 'rarely',
            r'\balways\b': 'typically',
        }
    
    def casual_to_formal(self, text):
        """Convert casual tone to formal"""
        result = text
        
        # Apply replacements
        for pattern, replacement in self.casual_formal_map.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Remove excessive punctuation
        result = re.sub(r'!+', '.', result)
        result = re.sub(r'\?+', '?', result)
        result = re.sub(r'\.{2,}', '.', result)
        
        # Capitalize sentences properly
        sentences = re.split(r'([.!?]\s+)', result)
        result = ''.join([s.capitalize() if i % 2 == 0 and s else s for i, s in enumerate(sentences)])
        
        # Add formal greeting if missing
        if not any(word in result.lower()[:50] for word in ['dear', 'hello', 'greetings']):
            result = 'Dear Sir/Madam,\n\n' + result
        
        # Add formal closing if missing
        if not any(word in result.lower()[-100:] for word in ['regards', 'sincerely', 'respectfully']):
            result += '\n\nBest regards,'
        
        return result
    
    def aggressive_to_diplomatic(self, text):
        """Convert aggressive tone to diplomatic"""
        result = text
        
        # Apply replacements
        for pattern, replacement in self.aggressive_diplomatic_map.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Remove all caps (shouting)
        sentences = result.split('.')
        result = '. '.join([s.capitalize() if s.isupper() and len(s.strip()) > 10 else s for s in sentences])
        
        # Add softening phrases
        if not any(word in result.lower() for word in ['please', 'kindly', 'appreciate', 'would']):
            result = 'I would appreciate your attention to the following matter.\n\n' + result
        
        # Replace harsh punctuation
        result = re.sub(r'!+', '.', result)
        
        return result
    
    def adjust_formality(self, text, level):
        """Adjust formality level (0-100)"""
        if level < 25:
            # Very casual
            return self._make_very_casual(text)
        elif level < 50:
            # Casual
            return self._make_casual(text)
        elif level < 75:
            # Slightly formal
            return self._make_slightly_formal(text)
        else:
            # Very formal
            return self.casual_to_formal(text)
    
    def _make_very_casual(self, text):
        """Make text very casual"""
        result = text
        result = re.sub(r'\bDear\b', 'Hey', result, flags=re.IGNORECASE)
        result = re.sub(r'\bHello\b', 'Hi', result, flags=re.IGNORECASE)
        result = re.sub(r'\bThank you\b', 'Thanks', result, flags=re.IGNORECASE)
        result = re.sub(r'\bBest regards\b', 'Cheers', result, flags=re.IGNORECASE)
        result = re.sub(r'\bSincerely\b', 'Best', result, flags=re.IGNORECASE)
        result = re.sub(r'\bplease\b', 'pls', result, flags=re.IGNORECASE)
        result = re.sub(r'\bI would appreciate\b', "I'd love", result, flags=re.IGNORECASE)
        result = re.sub(r'\bcannot\b', "can't", result, flags=re.IGNORECASE)
        result = re.sub(r'\bdo not\b', "don't", result, flags=re.IGNORECASE)
        result = re.sub(r'\bwill not\b', "won't", result, flags=re.IGNORECASE)
        result = re.sub(r'\bgoing to\b', 'gonna', result, flags=re.IGNORECASE)
        result = re.sub(r'\bwant to\b', 'wanna', result, flags=re.IGNORECASE)
        return result
    
    def _make_casual(self, text):
        """Make text casual"""
        result = text
        result = re.sub(r'\bDear\b', 'Hi', result, flags=re.IGNORECASE)
        result = re.sub(r'\bThank you very much\b', 'Thanks', result, flags=re.IGNORECASE)
        result = re.sub(r'\bThank you\b', 'Thanks', result, flags=re.IGNORECASE)
        result = re.sub(r'\bBest regards\b', 'Best', result, flags=re.IGNORECASE)
        result = re.sub(r'\bSincerely\b', 'Thanks', result, flags=re.IGNORECASE)
        result = re.sub(r'\bRespectfully\b', 'Best', result, flags=re.IGNORECASE)
        result = re.sub(r'\bI would appreciate\b', "I'd appreciate", result, flags=re.IGNORECASE)
        return result
    
    def _make_slightly_formal(self, text):
        """Make text slightly formal"""
        result = text
        result = re.sub(r'\bHey\b', 'Hello', result, flags=re.IGNORECASE)
        result = re.sub(r'\bHi\b', 'Hello', result, flags=re.IGNORECASE)
        result = re.sub(r'\bThanks\b', 'Thank you', result, flags=re.IGNORECASE)
        result = re.sub(r'\bCheers\b', 'Best regards', result, flags=re.IGNORECASE)
        result = re.sub(r'\bpls\b', 'please', result, flags=re.IGNORECASE)
        result = re.sub(r"\bcan't\b", 'cannot', result, flags=re.IGNORECASE)
        result = re.sub(r"\bdon't\b", 'do not', result, flags=re.IGNORECASE)
        result = re.sub(r"\bwon't\b", 'will not', result, flags=re.IGNORECASE)
        result = re.sub(r'\bgonna\b', 'going to', result, flags=re.IGNORECASE)
        result = re.sub(r'\bwanna\b', 'want to', result, flags=re.IGNORECASE)
        return result
    
    def preview_tone(self, text, conversion_type, formality_level=50):
        """Generate real-time preview of tone adjustment"""
        if conversion_type == 'casual_to_formal':
            return self.casual_to_formal(text)
        elif conversion_type == 'aggressive_to_diplomatic':
            return self.aggressive_to_diplomatic(text)
        elif conversion_type == 'formality_slider':
            return self.adjust_formality(text, formality_level)
        else:
            return text
