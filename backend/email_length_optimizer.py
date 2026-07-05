from textblob import TextBlob
import re

class EmailLengthOptimizer:
    def __init__(self):
        # Optimal email length ranges (in words)
        self.optimal_min = 50
        self.optimal_max = 200
        self.too_short = 30
        self.too_long = 300
    
    def analyze_length(self, text):
        """Analyze email length and provide recommendations"""
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = len(sentences)
        
        # Calculate average sentence length
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Determine status
        if word_count < self.too_short:
            status = "Too Short"
            color = "warning"
            recommendation = "Your email is very brief. Consider adding more context and details to ensure your message is clear."
        elif word_count < self.optimal_min:
            status = "Brief"
            color = "info"
            recommendation = "Your email is concise but could benefit from additional details or context."
        elif word_count <= self.optimal_max:
            status = "Optimal"
            color = "success"
            recommendation = "Your email length is perfect! It's detailed enough without being overwhelming."
        elif word_count <= self.too_long:
            status = "Lengthy"
            color = "info"
            recommendation = "Your email is getting long. Consider if all information is necessary or if it can be condensed."
        else:
            status = "Too Long"
            color = "danger"
            recommendation = "Your email is very long. Recipients may lose interest. Consider summarizing or breaking it into multiple emails."
        
        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "status": status,
            "color": color,
            "recommendation": recommendation,
            "optimal_range": f"{self.optimal_min}-{self.optimal_max} words"
        }
    
    def summarize_email(self, text):
        """Summarize a lengthy email to optimal length"""
        words = text.split()
        word_count = len(words)
        
        if word_count <= self.optimal_max:
            return text  # Already optimal or short
        
        # Extract sentences
        sentences = [s.strip() for s in re.split(r'([.!?]+)', text) if s.strip()]
        
        # Reconstruct sentences with punctuation
        full_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                full_sentences.append(sentences[i] + sentences[i + 1])
            else:
                full_sentences.append(sentences[i])
        
        # Keep first sentence (usually greeting/intro)
        # Keep last sentence (usually closing)
        # Summarize middle content
        
        if len(full_sentences) <= 3:
            return text
        
        result = []
        
        # Add greeting/opening
        result.append(full_sentences[0])
        
        # Add key middle sentences (those with important keywords)
        important_keywords = ['important', 'urgent', 'please', 'need', 'require', 'deadline', 
                            'request', 'question', 'issue', 'problem', 'meeting', 'schedule']
        
        middle_sentences = full_sentences[1:-1]
        important_middle = []
        
        for sentence in middle_sentences:
            if any(keyword in sentence.lower() for keyword in important_keywords):
                important_middle.append(sentence)
        
        # If no important sentences found, take first few middle sentences
        if not important_middle:
            important_middle = middle_sentences[:2]
        
        # Limit to 2-3 middle sentences
        result.extend(important_middle[:3])
        
        # Add closing
        result.append(full_sentences[-1])
        
        summarized = ' '.join(result)
        
        # Add note about summarization
        note = "\n\n[Note: This email has been summarized to improve readability. Original length: {} words, Summarized: {} words]".format(
            word_count, len(summarized.split())
        )
        
        return summarized + note
    
    def expand_email(self, text):
        """Expand a brief email with suggestions for additional content"""
        words = text.split()
        word_count = len(words)
        
        if word_count >= self.optimal_min:
            return text  # Already optimal or long
        
        # Analyze what's missing
        text_lower = text.lower()
        
        suggestions = []
        expanded_parts = []
        
        # Check for greeting
        has_greeting = any(word in text_lower[:50] for word in ['dear', 'hi', 'hello', 'hey', 'greetings'])
        if not has_greeting:
            expanded_parts.append("Dear [Recipient's Name],\n\n")
            suggestions.append("Added professional greeting")
        
        # Add the original text
        expanded_parts.append(text)
        
        # Check for context/background
        has_context = any(word in text_lower for word in ['because', 'since', 'as', 'regarding', 'about'])
        if not has_context:
            expanded_parts.append("\n\nThis is regarding [provide context/background information here].")
            suggestions.append("Added context section")
        
        # Check for specific details
        has_details = any(word in text_lower for word in ['specifically', 'details', 'particular', 'example'])
        if not has_details and word_count < 40:
            expanded_parts.append(" Specifically, [add relevant details or examples to clarify your message].")
            suggestions.append("Added details section")
        
        # Check for call to action
        has_action = any(word in text_lower for word in ['please', 'could you', 'would you', 'can you', 'let me know'])
        if not has_action:
            expanded_parts.append("\n\nPlease let me know if you need any additional information or have any questions.")
            suggestions.append("Added call to action")
        
        # Check for closing
        has_closing = any(word in text_lower[-100:] for word in ['regards', 'sincerely', 'best', 'thanks', 'thank you'])
        if not has_closing:
            expanded_parts.append("\n\nBest regards,\n[Your Name]")
            suggestions.append("Added professional closing")
        
        expanded = ''.join(expanded_parts)
        
        # Add note about expansion
        note = "\n\n[Note: This email has been expanded with suggestions. Original length: {} words, Expanded: {} words. Suggestions added: {}]".format(
            word_count, len(expanded.split()), ', '.join(suggestions)
        )
        
        return expanded + note
    
    def get_optimal_suggestion(self, text):
        """Get the optimal version of the email based on its length"""
        analysis = self.analyze_length(text)
        
        if analysis['status'] in ['Too Long', 'Lengthy']:
            return {
                'action': 'summarize',
                'original_length': analysis['word_count'],
                'optimized_text': self.summarize_email(text),
                'message': f"Email summarized from {analysis['word_count']} words to optimal length"
            }
        elif analysis['status'] in ['Too Short', 'Brief']:
            return {
                'action': 'expand',
                'original_length': analysis['word_count'],
                'optimized_text': self.expand_email(text),
                'message': f"Email expanded from {analysis['word_count']} words with helpful additions"
            }
        else:
            return {
                'action': 'none',
                'original_length': analysis['word_count'],
                'optimized_text': text,
                'message': "Email length is already optimal!"
            }
