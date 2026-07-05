import re
from textblob import TextBlob
from collections import Counter
import os
import json

class EmailAnalyzer:
    def __init__(self):
        self.formal_words = {'please', 'kindly', 'regards', 'sincerely', 'respectfully', 'appreciate', 'grateful'}
        self.urgent_words = {'urgent', 'asap', 'immediately', 'critical', 'emergency', 'priority'}
        self.action_verbs = {'send', 'provide', 'review', 'approve', 'confirm', 'schedule', 'update', 'complete'}
        self.rude_words = {'stupid', 'idiot', 'dumb', 'useless', 'incompetent', 'pathetic', 'ridiculous', 'waste'}
        
        # Check if AI is available
        self.has_ai = bool(os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))
        if self.has_ai:
            self.api_type = "groq" if os.getenv("GROQ_API_KEY") else "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"
            self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    def analyze(self, email_text):
        blob = TextBlob(email_text)
        
        # Basic metrics
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Enhanced analysis
        grammar_issues = self._check_grammar(email_text, blob)
        structure_analysis = self._analyze_structure(email_text)
        professionalism_score = self._calculate_professionalism(email_text, polarity)
        
        # Tone analysis
        tone = self._detect_tone(email_text, polarity)
        tone_analysis = self._get_detailed_tone_analysis(tone, email_text, polarity)
        
        # Intent detection
        intent, confidence = self._detect_intent(email_text)
        
        # Sentiment
        sentiment = "Positive" if polarity > 0.1 else "Negative" if polarity < -0.1 else "Neutral"
        
        # Emotion
        emotion = self._detect_emotion(email_text, polarity)
        
        # Key points
        key_points = self._extract_key_points(email_text)
        
        # Action items
        action_items = self._extract_action_items(email_text)
        
        # Priority
        priority, priority_reason = self._detect_priority(email_text)
        
        # Summary
        summary = self._generate_summary(email_text, intent, tone)
        
        # Key problems
        key_problems = self._identify_key_problems(email_text, tone, grammar_issues, structure_analysis)
        
        # Suggestions
        suggestions = self._generate_suggestions(key_problems, tone, grammar_issues)
        
        # Suggested reply
        if self.has_ai:
            suggested_reply = self._generate_ai_reply(email_text, intent, tone, sentiment)
        else:
            suggested_reply = self._generate_smart_reply(email_text, intent, tone)
        
        # Email suggestion (improved version of the original email)
        email_suggestion = None
        if self.has_ai:
            email_suggestion = self._generate_ai_professional_rewrite(email_text, tone, intent, sentiment)
        if not email_suggestion:
            email_suggestion = self._generate_professional_rewrite(email_text, tone, intent, sentiment, key_problems)
        
        # Email Scoring System
        email_scores = self._calculate_email_scores(email_text, blob, tone, intent, sentiment, polarity, grammar_issues, structure_analysis, professionalism_score)
        
        return {
            "summary": summary,
            "tone": tone,
            "tone_reasoning": self._get_tone_reasoning(tone, email_text),
            "tone_analysis": tone_analysis,
            "intent": intent,
            "confidence": f"{confidence}%",
            "sentiment": sentiment,
            "polarity": round(polarity, 2),
            "subjectivity": round(subjectivity, 2),
            "emotion": emotion,
            "grammar_issues": grammar_issues,
            "structure_analysis": structure_analysis,
            "professionalism_score": professionalism_score,
            "key_points": key_points,
            "key_problems": key_problems,
            "suggestions": suggestions,
            "action_items": action_items,
            "priority": priority,
            "priority_reason": priority_reason,
            "email_suggestion": email_suggestion,
            "suggested_reply": suggested_reply,
            "email_scores": email_scores
        }
    
    
    def _check_grammar(self, text, blob):
        """Check for grammar and spelling issues"""
        issues = []
        
        # Common abbreviations and technical terms to ignore
        ignore_words = {
            'asap', 'fyi', 'btw', 'etc', 'vs', 'ie', 'eg', 'rsvp', 'ceo', 'cto', 'cfo',
            'hr', 'it', 'pr', 'qa', 'ui', 'ux', 'api', 'url', 'pdf', 'doc', 'ppt',
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'jan', 'feb', 'mar', 'apr',
            'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'am', 'pm',
            'usa', 'uk', 'eu', 'usd', 'eur', 'gbp', 'inc', 'ltd', 'llc', 'corp',
            'mr', 'mrs', 'ms', 'dr', 'prof', 'st', 'ave', 'blvd', 'dept', 'mgr',
            'asst', 'dir', 'vp', 'svp', 'evp', 'jr', 'sr', 'phd', 'mba', 'ba', 'bs',
            'ok', 'okay', 'yeah', 'yep', 'nope', 'gonna', 'wanna', 'gotta',
            'covid', 'wifi', 'email', 'online', 'offline', 'login', 'logout', 'signup'
        }
        
        # Check spelling with improved filtering
        words = blob.words
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Skip if:
            # 1. Too short (likely abbreviation)
            if len(word) <= 2:
                continue
            
            # 2. Not alphabetic (numbers, symbols)
            if not word.isalpha():
                continue
            
            # 3. In ignore list
            if word_lower in ignore_words:
                continue
            
            # 4. Starts with capital (likely proper noun/name)
            # But check if it's at start of sentence
            is_sentence_start = i == 0 or (i > 0 and str(words[i-1]).endswith(('.', '!', '?')))
            if word[0].isupper() and not is_sentence_start:
                continue  # Skip proper nouns (names, places, companies)
            
            # 5. All caps (likely acronym)
            if word.isupper() and len(word) > 1:
                continue
            
            # 6. Contains numbers (like "2nd", "3rd")
            if any(char.isdigit() for char in word):
                continue
            
            # Now check spelling
            try:
                corrected = str(TextBlob(word).correct())
                # Only flag if correction is significantly different
                if corrected.lower() != word_lower and len(word) > 3:
                    # Additional check: if word is capitalized, corrected should be too
                    if word[0].isupper() and corrected[0].islower():
                        continue  # Skip, likely a proper noun
                    
                    # Check if it's a common word variation
                    if self._is_common_variation(word_lower, corrected.lower()):
                        continue
                    
                    issues.append({
                        "wrong": word,
                        "correct": corrected,
                        "type": "spelling"
                    })
            except:
                pass  # Skip if correction fails
        
        # Check for common grammar issues
        text_lower = text.lower()
        
        # Missing punctuation at end
        if text.strip() and text.strip()[-1] not in '.!?':
            issues.append({
                "wrong": "Missing punctuation at end",
                "correct": "Add period, exclamation, or question mark",
                "type": "punctuation"
            })
        
        # Multiple spaces
        if '  ' in text:
            issues.append({
                "wrong": "Multiple consecutive spaces",
                "correct": "Use single space between words",
                "type": "spacing"
            })
        
        # All caps (shouting) - but allow short all-caps words (acronyms)
        sentences = text.split('.')
        for sentence in sentences:
            sentence_stripped = sentence.strip()
            if len(sentence_stripped) > 15 and sentence_stripped.isupper():
                # Check if it's not just acronyms
                words_in_sentence = sentence_stripped.split()
                long_words = [w for w in words_in_sentence if len(w) > 3]
                if len(long_words) > 2:  # Multiple long words in caps
                    issues.append({
                        "wrong": sentence_stripped[:50] + "...",
                        "correct": "Avoid writing in all caps (use proper capitalization)",
                        "type": "formatting"
                    })
                    break  # Only report once
        
        # Common grammar mistakes
        grammar_patterns = [
            (r"\bi\s", "I ", "Capitalize 'I' when used as pronoun"),
            (r"\bim\b", "I'm", "Use apostrophe in contractions"),
            (r"\bdont\b", "don't", "Use apostrophe in contractions"),
            (r"\bcant\b", "can't", "Use apostrophe in contractions"),
            (r"\bwont\b", "won't", "Use apostrophe in contractions"),
            (r"\bisnt\b", "isn't", "Use apostrophe in contractions"),
            (r"\barent\b", "aren't", "Use apostrophe in contractions"),
        ]
        
        for pattern, correction, message in grammar_patterns:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                if match:
                    issues.append({
                        "wrong": match.group(0),
                        "correct": correction,
                        "type": "grammar"
                    })
        
        return issues[:8]  # Limit to 8 most important issues
    
    def _is_common_variation(self, word1, word2):
        """Check if two words are common variations (e.g., color/colour)"""
        common_variations = [
            ('color', 'colour'), ('favor', 'favour'), ('honor', 'honour'),
            ('labor', 'labour'), ('neighbor', 'neighbour'), ('flavor', 'flavour'),
            ('organize', 'organise'), ('realize', 'realise'), ('recognize', 'recognise'),
            ('analyze', 'analyse'), ('center', 'centre'), ('meter', 'metre'),
            ('theater', 'theatre'), ('fiber', 'fibre'), ('liter', 'litre')
        ]
        
        for var1, var2 in common_variations:
            if (word1 == var1 and word2 == var2) or (word1 == var2 and word2 == var1):
                return True
        return False
    
    def _analyze_structure(self, text):
        """Analyze email structure"""
        has_greeting = any(word in text.lower()[:100] for word in ['dear', 'hi', 'hello', 'hey', 'greetings'])
        has_closing = any(word in text.lower()[-200:] for word in ['regards', 'sincerely', 'best', 'thanks', 'thank you'])
        has_body = len(text.split()) > 20
        
        issues = []
        if not has_greeting:
            issues.append("Missing greeting")
        if not has_closing:
            issues.append("Missing closing")
        if not has_body:
            issues.append("Email body is too short")
        
        if not issues:
            return "Well-structured email with greeting, body, and closing."
        else:
            return "Structure issues: " + ", ".join(issues) + "."
    
    def _calculate_professionalism(self, text, polarity):
        """Calculate professionalism score out of 10 with detailed breakdown"""
        score = 10
        text_lower = text.lower()
        deductions = []
        additions = []
        
        # Deduct for rude words
        rude_count = sum(1 for word in self.rude_words if word in text_lower)
        if rude_count > 0:
            deduction = rude_count * 2
            score -= deduction
            deductions.append(f"Inappropriate language (-{deduction})")
        
        # Deduct for all caps
        if text.isupper() and len(text) > 20:
            score -= 3
            deductions.append("All caps text (-3)")
        
        # Deduct for very negative polarity
        if polarity < -0.5:
            score -= 2
            deductions.append("Very negative tone (-2)")
        elif polarity < -0.2:
            score -= 1
            deductions.append("Negative tone (-1)")
        
        # Deduct for missing structure
        has_greeting = any(word in text_lower[:100] for word in ['dear', 'hi', 'hello'])
        has_closing = any(word in text_lower[-200:] for word in ['regards', 'sincerely', 'best'])
        if not has_greeting:
            score -= 1
            deductions.append("Missing greeting (-1)")
        if not has_closing:
            score -= 1
            deductions.append("Missing closing (-1)")
        
        # Deduct for excessive exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            score -= 1
            deductions.append(f"Excessive exclamation marks (-1)")
        
        # Deduct for poor grammar indicators
        if '  ' in text:  # Multiple spaces
            score -= 0.5
            deductions.append("Formatting issues (-0.5)")
        
        # Add for formal words
        formal_count = sum(1 for word in self.formal_words if word in text_lower)
        if formal_count > 0:
            addition = min(formal_count, 2)
            score += addition
            additions.append(f"Professional language (+{addition})")
        
        # Add for proper structure
        if has_greeting and has_closing:
            score += 0.5
            additions.append("Complete structure (+0.5)")
        
        # Add for positive polarity
        if polarity > 0.3:
            score += 0.5
            additions.append("Positive tone (+0.5)")
        
        final_score = max(1, min(10, score))
        
        return round(final_score, 1)
    
    def _get_detailed_tone_analysis(self, tone, text, polarity):
        """Provide detailed tone analysis"""
        text_lower = text.lower()
        
        analysis = f"The email has a {tone.lower()} tone. "
        
        if tone == "Negative" or polarity < -0.3:
            rude_found = [word for word in self.rude_words if word in text_lower]
            if rude_found:
                analysis += f"Contains inappropriate language: {', '.join(rude_found)}. "
            analysis += "The negative tone may damage professional relationships and should be revised."
        elif tone == "Formal":
            analysis += "Professional language is used appropriately for business communication."
        elif tone == "Friendly":
            analysis += "Warm and approachable while maintaining professionalism."
        elif tone == "Apologetic":
            analysis += "Shows accountability and willingness to make amends."
        else:
            analysis += "Straightforward communication without strong emotional content."
        
        return analysis
    
    def _identify_key_problems(self, text, tone, grammar_issues, structure_analysis):
        """Identify main problems in the email"""
        problems = []
        text_lower = text.lower()
        
        # Tone problems
        if tone == "Negative":
            problems.append("Negative or confrontational tone")
        
        # Rude language
        rude_found = [word for word in self.rude_words if word in text_lower]
        if rude_found:
            problems.append(f"Inappropriate language used: {', '.join(rude_found)}")
        
        # Grammar issues
        if len(grammar_issues) > 0:
            problems.append(f"{len(grammar_issues)} grammar/spelling issues detected")
        
        # Structure issues
        if "issues" in structure_analysis.lower():
            problems.append("Missing proper email structure")
        
        # All caps
        if text.isupper() and len(text) > 20:
            problems.append("Written in all caps (appears as shouting)")
        
        # No greeting or closing
        has_greeting = any(word in text_lower[:100] for word in ['dear', 'hi', 'hello'])
        has_closing = any(word in text_lower[-200:] for word in ['regards', 'sincerely', 'best'])
        if not has_greeting:
            problems.append("Missing greeting")
        if not has_closing:
            problems.append("Missing professional closing")
        
        return problems if problems else ["No major issues detected"]
    
    def _generate_suggestions(self, key_problems, tone, grammar_issues):
        """Generate actionable suggestions"""
        suggestions = []
        
        if "Negative" in tone or any("tone" in p.lower() for p in key_problems):
            suggestions.append("Rewrite with a neutral or positive tone")
            suggestions.append("Remove blame language and focus on solutions")
        
        if any("inappropriate" in p.lower() or "language" in p.lower() for p in key_problems):
            suggestions.append("Replace unprofessional words with respectful alternatives")
        
        if len(grammar_issues) > 0:
            suggestions.append("Correct spelling and grammar errors before sending")
        
        if any("greeting" in p.lower() for p in key_problems):
            suggestions.append("Add a proper greeting (e.g., 'Dear [Name]' or 'Hi [Name]')")
        
        if any("closing" in p.lower() for p in key_problems):
            suggestions.append("Add a professional closing (e.g., 'Best regards' or 'Sincerely')")
        
        if any("caps" in p.lower() for p in key_problems):
            suggestions.append("Use proper capitalization instead of all caps")
        
        if not suggestions:
            suggestions.append("Email is well-written, consider adding more specific details if needed")
        
        return suggestions
    
    def _generate_professional_rewrite(self, text, tone, intent, sentiment, key_problems):
        """Generate a professional rewrite of the email"""
        text_lower = text.lower()
        
        # If email is already professional, return improved version
        if tone == "Formal" and len(key_problems) == 1 and "No major issues" in key_problems[0]:
            return self._generate_email_suggestion(text, tone, intent, sentiment)
        
        # Extract core message
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        topics = self._extract_topics(text)
        
        parts = []
        
        # Professional greeting
        parts.append("Dear [Recipient's Name],\n\n")
        
        # Opening based on intent
        if intent == "Complaint":
            parts.append("I hope this message finds you well. I am writing to bring to your attention a concern regarding ")
        elif intent == "Request":
            parts.append("I hope you are doing well. I am reaching out to kindly request your assistance with ")
        elif intent == "Follow-up":
            parts.append("I hope this email finds you well. I wanted to follow up on our previous discussion regarding ")
        else:
            parts.append("I hope this message finds you well. I am writing to discuss ")
        
        # Add topic
        if topics:
            parts.append(f"{topics[0]}.\n\n")
        else:
            parts.append("the matter at hand.\n\n")
        
        # Main content (cleaned up)
        if sentences:
            # Remove rude words and negative language
            clean_sentence = sentences[0]
            for rude_word in self.rude_words:
                clean_sentence = re.sub(r'\b' + rude_word + r'\b', 'concerning', clean_sentence, flags=re.IGNORECASE)
            parts.append(f"{clean_sentence}.\n\n")
        
        # Professional closing based on intent
        if intent == "Complaint":
            parts.append("I would greatly appreciate your prompt attention to this matter. Please let me know how we can resolve this situation.\n\n")
        elif intent == "Request":
            parts.append("I would be grateful for your assistance with this matter. Please let me know if you need any additional information.\n\n")
        else:
            parts.append("I look forward to your response and am happy to discuss this further if needed.\n\n")
        
        # Sign off
        parts.append("Thank you for your time and consideration.\n\nBest regards,\n[Your Name]")
        
        return "".join(parts)
    
    def _detect_tone(self, text, polarity):
        text_lower = text.lower()
        formal_count = sum(1 for word in self.formal_words if word in text_lower)
        
        if formal_count >= 2:
            return "Formal"
        elif polarity > 0.3:
            return "Friendly"
        elif polarity < -0.3:
            return "Negative"
        elif any(word in text_lower for word in ['sorry', 'apologize', 'regret']):
            return "Apologetic"
        else:
            return "Neutral"
    
    def _get_tone_reasoning(self, tone, text):
        reasons = {
            "Formal": "Uses professional language and courteous expressions",
            "Friendly": "Positive language with warm, approachable phrasing",
            "Negative": "Contains critical or dissatisfied language",
            "Apologetic": "Expresses regret or seeks to make amends",
            "Neutral": "Straightforward communication without strong emotion"
        }
        return reasons.get(tone, "Standard professional communication")
    
    def _detect_intent(self, text):
        text_lower = text.lower()
        
        intents = {
            "Request": ['could you', 'can you', 'please send', 'need', 'require', 'request'],
            "Inquiry": ['?', 'wondering', 'question', 'clarify', 'information about'],
            "Complaint": ['disappointed', 'unsatisfied', 'issue', 'problem', 'concern'],
            "Follow-up": ['following up', 'checking in', 'any update', 'status'],
            "Confirmation": ['confirm', 'verified', 'agreed', 'acknowledged'],
            "Meeting Request": ['meeting', 'schedule', 'call', 'discuss', 'available'],
            "Thank You": ['thank', 'appreciate', 'grateful', 'thanks']
        }
        
        scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[intent] = score
        
        if scores:
            detected_intent = max(scores, key=scores.get)
            confidence = min(70 + scores[detected_intent] * 10, 95)
            return detected_intent, confidence
        
        return "Informational", 60
    
    def _detect_emotion(self, text, polarity):
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['excited', 'happy', 'great', 'excellent', 'wonderful']):
            return "Happy"
        elif any(word in text_lower for word in ['angry', 'frustrated', 'unacceptable', 'furious']):
            return "Angry"
        elif any(word in text_lower for word in ['sad', 'disappointed', 'unfortunate', 'regret']):
            return "Sad"
        elif any(word in text_lower for word in ['worried', 'concerned', 'anxious']):
            return "Anxious"
        elif polarity > 0.2:
            return "Positive"
        elif polarity < -0.2:
            return "Negative"
        else:
            return "Neutral"
    
    def _extract_key_points(self, text):
        sentences = text.split('.')
        key_points = []
        
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 20:
                key_points.append(sentence)
        
        return key_points[:4] if key_points else ["Main content of the email"]
    
    def _extract_action_items(self, text):
        text_lower = text.lower()
        action_items = []
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            for verb in self.action_verbs:
                if verb in sentence_lower:
                    action_items.append({
                        "action": sentence.strip(),
                        "responsibility": "Recipient" if any(word in sentence_lower for word in ['you', 'your']) else "Sender"
                    })
                    break
        
        return action_items[:3] if action_items else []
    
    def _detect_priority(self, text):
        text_lower = text.lower()
        
        urgent_count = sum(1 for word in self.urgent_words if word in text_lower)
        
        if urgent_count >= 2 or 'critical' in text_lower:
            return "Critical", "Contains multiple urgent indicators"
        elif urgent_count == 1 or 'important' in text_lower:
            return "High", "Marked as urgent or important"
        elif any(word in text_lower for word in ['deadline', 'due', 'by']):
            return "Medium", "Contains time-sensitive elements"
        else:
            return "Low", "Standard communication without urgency"
    
    def _generate_summary(self, text, intent, tone):
        """Generate intelligent summary based on email content"""
        # Get first few sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        
        # Extract key information
        text_lower = text.lower()
        has_deadline = any(word in text_lower for word in ['deadline', 'by', 'before', 'until'])
        has_attachment = any(word in text_lower for word in ['attach', 'document', 'file'])
        is_urgent = any(word in text_lower for word in ['urgent', 'asap', 'immediately'])
        
        # Build summary
        summary_parts = []
        
        # Add intent description
        if intent == "Request":
            summary_parts.append("Sender is requesting")
        elif intent == "Inquiry":
            summary_parts.append("Sender is inquiring about")
        elif intent == "Complaint":
            summary_parts.append("Sender is expressing concern regarding")
        elif intent == "Follow-up":
            summary_parts.append("Sender is following up on")
        elif intent == "Meeting Request":
            summary_parts.append("Sender is requesting a meeting to discuss")
        elif intent == "Thank You":
            summary_parts.append("Sender is expressing gratitude for")
        else:
            summary_parts.append("Sender is communicating about")
        
        # Add main content (first meaningful sentence)
        if sentences:
            main_content = sentences[0][:100]
            if len(sentences[0]) > 100:
                main_content += "..."
            summary_parts.append(main_content.lower())
        
        # Add urgency/deadline info
        if is_urgent:
            summary_parts.append("This is marked as urgent.")
        elif has_deadline:
            summary_parts.append("Time-sensitive matter with deadline.")
        
        if has_attachment:
            summary_parts.append("Includes attachments.")
        
        return " ".join(summary_parts)
    
    def _generate_reply(self, text, intent, tone):
        """Generate highly contextual and intelligent reply based on actual email content"""
        text_lower = text.lower()
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
        
        # Extract sender name from signature (last few lines)
        sender_name = None
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in reversed(lines[-5:]):
            words = line.split()
            for word in words:
                if word and len(word) > 2 and word[0].isupper() and word.isalpha():
                    if word.lower() not in ['dear', 'hi', 'hello', 'regards', 'sincerely', 'best', 'thanks', 'thank', 'sir', 'madam', 'team', 'support']:
                        sender_name = word
                        break
            if sender_name:
                break
        
        # Deep content analysis
        has_question = '?' in text
        questions = [s.strip() + '?' for s in text.split('?')[:-1] if s.strip()]
        has_deadline = any(word in text_lower for word in ['deadline', 'by', 'before', 'until', 'due'])
        has_attachment = any(word in text_lower for word in ['attach', 'document', 'file', 'pdf', 'report'])
        is_urgent = any(word in text_lower for word in ['urgent', 'asap', 'immediately', 'critical', 'priority'])
        has_thanks = any(word in text_lower for word in ['thank', 'appreciate', 'grateful'])
        has_apology = any(word in text_lower for word in ['sorry', 'apologize', 'regret'])
        has_problem = any(word in text_lower for word in ['issue', 'problem', 'concern', 'trouble', 'difficulty', 'disappointed'])
        
        # Extract specific requests/actions from email
        action_phrases = []
        for sentence in sentences:
            sent_lower = sentence.lower()
            if any(word in sent_lower for word in ['could you', 'can you', 'please', 'need', 'require', 'would like', 'want']):
                action_phrases.append(sentence)
        
        # Extract topics/subjects mentioned
        topics = self._extract_topics(text)
        main_topic = topics[0] if topics else 'this matter'
        
        # Build highly contextual reply
        reply_parts = []
        
        # === OPENING ===
        if sender_name:
            reply_parts.append(f"Hi {sender_name},\n\n")
        else:
            reply_parts.append("Hi there,\n\n")
        
        # === ACKNOWLEDGMENT ===
        if has_thanks:
            reply_parts.append("Thank you for your email. ")
        elif has_apology:
            reply_parts.append("Thank you for reaching out and for your honesty. ")
        elif is_urgent:
            reply_parts.append("Thank you for bringing this urgent matter to my attention. ")
        elif intent == "Complaint":
            reply_parts.append("Thank you for sharing your concerns with me. ")
        else:
            reply_parts.append("Thank you for your message. ")
        
        reply_parts.append("\n\n")
        
        # === MAIN RESPONSE BASED ON INTENT ===
        if intent == "Request":
            if action_phrases:
                reply_parts.append(f"I understand you need assistance with {main_topic}. ")
            
            if is_urgent:
                reply_parts.append("Given the urgent nature of your request, I will prioritize this and get back to you within 24 hours. ")
            elif has_deadline:
                reply_parts.append("I acknowledge the deadline and will ensure everything is completed on time. ")
            else:
                reply_parts.append("I will review this carefully and provide you with a detailed response shortly. ")
            
            if has_attachment:
                reply_parts.append("I have received the attached documents and will review them thoroughly. ")
        
        elif intent == "Inquiry":
            if questions:
                reply_parts.append(f"Regarding your question about {main_topic}: ")
                reply_parts.append("\n\n[Provide detailed answer addressing the specific question raised in the email.] ")
            else:
                reply_parts.append(f"Regarding your inquiry about {main_topic}: ")
                reply_parts.append("\n\n[Provide comprehensive information addressing the points raised.] ")
            
            reply_parts.append("\n\nIf you need any additional clarification, please don't hesitate to ask. ")
        
        elif intent == "Complaint":
            reply_parts.append("I sincerely apologize for the inconvenience and frustration you've experienced. ")
            
            if has_problem:
                reply_parts.append(f"Regarding the issue with {main_topic}, I am immediately looking into this matter. ")
            
            reply_parts.append("I take full responsibility for resolving this and will keep you updated on the progress. ")
            reply_parts.append("You can expect an update from me within 24-48 hours. ")
        
        elif intent == "Follow-up":
            reply_parts.append(f"Thank you for following up on {main_topic}. ")
            reply_parts.append("I apologize for the delay in my response. ")
            reply_parts.append("[Provide status update and next steps.] ")
        
        elif intent == "Meeting Request":
            reply_parts.append("I would be happy to meet and discuss this further. ")
            reply_parts.append("I am available [suggest specific times/dates]. ")
            reply_parts.append("Please let me know what works best for you, and I'll send a calendar invite. ")
        
        elif intent == "Thank You":
            reply_parts.append("You're very welcome! ")
            reply_parts.append("I'm glad I could help. ")
            reply_parts.append("Please don't hesitate to reach out if you need anything else. ")
        
        elif intent == "Confirmation":
            reply_parts.append("Thank you for the confirmation. ")
            reply_parts.append("I have noted this and will proceed accordingly. ")
        
        else:  # Informational
            reply_parts.append(f"Thank you for the information about {main_topic}. ")
            reply_parts.append("I have reviewed the details and will take appropriate action. ")
        
        # === CLOSING ===
        reply_parts.append("\n\nPlease let me know if you have any questions or need further assistance.\n\n")
        reply_parts.append("Best regards,\n[Your Name]")
        
        return "".join(reply_parts)

    
    def _extract_topics(self, text):
        """Extract main topics/subjects from email"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'our', 'their'}
        
        words = text.lower().split()
        # Get noun phrases (2-3 word combinations that might be topics)
        topics = []
        
        for i in range(len(words) - 1):
            if words[i] not in stop_words and words[i+1] not in stop_words:
                if len(words[i]) > 3 and len(words[i+1]) > 3:
                    topics.append(f"{words[i]} {words[i+1]}")
        
        # Also look for capitalized words (likely important nouns)
        sentences = text.split('.')
        for sentence in sentences:
            words_in_sent = sentence.split()
            for word in words_in_sent:
                if word and word[0].isupper() and word.lower() not in stop_words and len(word) > 3:
                    if word not in ['Dear', 'Hi', 'Hello', 'Thanks', 'Thank', 'Please', 'Regards', 'Best', 'Sincerely']:
                        topics.append(word.lower())
        
        return topics[:3] if topics else ["the matter discussed"]
    
    def _generate_ai_reply(self, email_text, intent, tone, sentiment):
        """Generate AI-powered professional email reply"""
        try:
            if self.api_type == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                
                prompt = f"""You are a professional email writing assistant. Generate a complete, professional, ready-to-send email reply to the following email.

Original Email:
{email_text}

Email Analysis:
- Intent: {intent}
- Tone: {tone}
- Sentiment: {sentiment}

Instructions:
1. Write a complete professional email reply
2. Match the tone of the original email
3. Address all points raised in the original email
4. Be specific and actionable (no placeholders like [Name] or [Date])
5. Use proper email format with greeting and closing
6. Keep it concise but comprehensive
7. Make it ready to send (the user should only need to add their name)

Generate the reply now:"""
                
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                return response.content[0].text.strip()
            
            elif self.api_type == "openai":
                import openai
                openai.api_key = self.api_key
                
                prompt = f"""Generate a complete, professional, ready-to-send email reply to this email:

{email_text}

Analysis: Intent={intent}, Tone={tone}, Sentiment={sentiment}

Requirements:
- Complete professional reply
- Match the original tone
- Address all points
- No placeholders
- Proper format
- Ready to send"""
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a professional email writing assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500
                )
                
                return response.choices[0].message.content.strip()
            
            elif self.api_type == "groq":
                from openai import OpenAI
                client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.groq.com/openai/v1",
                )
                
                prompt = f"""Generate a complete, professional, ready-to-send email reply to this email:

{email_text}

Analysis: Intent={intent}, Tone={tone}, Sentiment={sentiment}

Requirements:
- Complete professional reply
- Match the original tone
- Address all points
- No placeholders
- Proper format
- Ready to send"""
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a professional email writing assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500
                )
                
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"AI Reply Error: {e}")
            return self._generate_smart_reply(email_text, intent, tone)
            
    def _generate_ai_professional_rewrite(self, email_text, tone, intent, sentiment):
        """Generate a perfectly related professional rewrite of the email using AI"""
        try:
            prompt = f"""You are a professional email editor. Rewrite the following email to be perfectly professional, polite, clear, and effective.
It is CRITICAL that your rewrite is perfectly related to the original email and preserves all its context, facts, and intent. 
Do not hallucinate new details, but do improve the structure, grammar, and tone.

Original Email:
{email_text}

Analysis: Intent={intent}, Tone={tone}, Sentiment={sentiment}

Please provide ONLY the rewritten email, ready to send."""

            if self.api_type == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            
            elif self.api_type in ["openai", "groq"]:
                if self.api_type == "groq":
                    from openai import OpenAI
                    client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")
                    model = "llama-3.3-70b-versatile"
                else:
                    import openai
                    client = openai
                    client.api_key = self.api_key
                    model = "gpt-4"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert professional email rewriter."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Rewrite Error: {e}")
            return None
    
    def _generate_email_suggestion(self, text, tone, intent, sentiment):
        """Generate an improved/rewritten version of the original email based on actual content"""
        text_lower = text.lower()
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
        
        # Extract sender name from signature (last few lines)
        sender_name = None
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in reversed(lines[-5:]):
            words = line.split()
            for word in words:
                if word and len(word) > 2 and word[0].isupper() and word.isalpha():
                    if word.lower() not in ['dear', 'hi', 'hello', 'regards', 'sincerely', 'best', 'thanks', 'thank', 'sir', 'madam', 'team', 'support']:
                        sender_name = word
                        break
            if sender_name:
                break
        
        # Analyze email characteristics
        has_greeting = any(word in text_lower[:100] for word in ['dear', 'hi', 'hello', 'hey'])
        has_closing = any(word in text_lower[-200:] for word in ['regards', 'sincerely', 'best', 'thanks'])
        has_apology = any(w in text_lower for w in ['sorry', 'apologize', 'regret'])
        is_negative = tone == "Negative" or sentiment == "Negative"
        has_casual = any(phrase in text_lower for phrase in ['kind of', 'sort of', 'i guess', 'maybe', 'probably', 'stuff', 'thing'])
        
        # Extract topics and main content
        topics = self._extract_topics(text)
        main_topic = topics[0] if topics else 'the matter at hand'
        
        # Clean up sentences - remove casual language
        cleaned_sentences = []
        for sentence in sentences:
            clean = sentence
            # Replace casual phrases with professional ones
            clean = re.sub(r'\bkind of\b', 'somewhat', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bsort of\b', 'somewhat', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bstuff\b', 'matters', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bthing\b', 'matter', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\banyway\b', '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bi guess\b', 'I believe', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bprobably\b', 'likely', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bmaybe\b', 'perhaps', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bgonna\b', 'going to', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\bwanna\b', 'want to', clean, flags=re.IGNORECASE)
            
            # Remove rude words
            for rude_word in self.rude_words:
                clean = re.sub(r'\b' + rude_word + r'\b', 'concerning', clean, flags=re.IGNORECASE)
            
            if clean.strip():
                cleaned_sentences.append(clean.strip())
        
        # Build improved email
        parts = []
        
        # Add greeting if missing
        if not has_greeting:
            parts.append("Dear Sir/Madam,\n\n")
        else:
            # Keep original greeting but make it professional
            for line in text.split('\n')[:3]:
                if any(word in line.lower() for word in ['dear', 'hi', 'hello']):
                    if 'hi' in line.lower() or 'hello' in line.lower():
                        # Extract recipient name if present
                        words = line.split()
                        recipient = None
                        for i, word in enumerate(words):
                            if word.lower() in ['hi', 'hello'] and i + 1 < len(words):
                                next_word = words[i + 1].strip(',').strip()
                                if next_word and next_word[0].isupper():
                                    recipient = next_word
                                    break
                        if recipient:
                            parts.append(f"Dear {recipient},\n\n")
                        else:
                            parts.append("Dear Sir/Madam,\n\n")
                    else:
                        parts.append(f"{line.strip()}\n\n")
                    break
        
        # Add professional opening based on intent
        if not has_apology and (is_negative or intent == "Complaint"):
            parts.append("I hope this message finds you well. ")
        elif intent == "Request":
            parts.append("I hope you are doing well. ")
        elif intent == "Follow-up":
            parts.append("I hope this email finds you well. ")
        else:
            parts.append("I hope this message finds you well. ")
        
        # Add main content
        if intent == "Request":
            parts.append(f"I am writing to kindly request your assistance with {main_topic}. ")
        elif intent == "Inquiry":
            parts.append(f"I am writing to inquire about {main_topic}. ")
        elif intent == "Complaint":
            parts.append(f"I am writing to bring to your attention a concern regarding {main_topic}. ")
        elif intent == "Follow-up":
            parts.append(f"I wanted to follow up on our previous discussion regarding {main_topic}. ")
        elif intent == "Meeting Request":
            parts.append(f"I would like to schedule a meeting to discuss {main_topic}. ")
        elif intent == "Thank You":
            parts.append(f"I wanted to express my sincere gratitude for {main_topic}. ")
        else:
            parts.append(f"I am writing regarding {main_topic}. ")
        
        parts.append("\n\n")
        
        # Add cleaned main content (skip first sentence if redundant)
        for i, sentence in enumerate(cleaned_sentences):
            # Skip greeting/closing sentences
            sent_lower = sentence.lower()
            if any(word in sent_lower for word in ['dear', 'hi', 'hello', 'regards', 'sincerely', 'best', 'thanks']):
                continue
            if i < 3:  # Only include first 3 meaningful sentences
                parts.append(f"{sentence}. ")
        
        parts.append("\n\n")
        
        # Add professional closing based on intent
        if intent == "Request":
            parts.append("I would be grateful for your assistance with this matter. Please let me know if you need any additional information.\n\n")
        elif intent == "Inquiry":
            parts.append("I would appreciate your response at your earliest convenience. Please let me know if you need any clarification.\n\n")
        elif intent == "Complaint":
            parts.append("I would greatly appreciate your prompt attention to this matter. Please let me know how we can resolve this situation.\n\n")
        elif intent == "Follow-up":
            parts.append("I look forward to your response and am happy to discuss this further if needed.\n\n")
        elif intent == "Meeting Request":
            parts.append("Please let me know your availability, and I will arrange a suitable time. I look forward to our discussion.\n\n")
        else:
            parts.append("I look forward to your response. Please feel free to contact me if you have any questions.\n\n")
        
        # Add closing if missing
        if not has_closing:
            parts.append("Thank you for your time and consideration.\n\n")
        
        parts.append("Best regards,\n")
        parts.append(sender_name if sender_name else "[Your Name]")
        
        return "".join(parts)
    
    def _generate_smart_reply(self, text, intent, tone):
        """Generate intelligent rule-based reply (fallback when no AI)"""
        return self._generate_reply(text, intent, tone)
    
    def _calculate_email_scores(self, text, blob, tone, intent, sentiment, polarity, grammar_issues, structure_analysis, professionalism_score):
        """Calculate comprehensive email quality scores"""
        
        # 1. Readability Score (0-100)
        words = text.split()
        sentences = [s for s in text.split('.') if len(s.strip()) > 5]
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        readability = 100
        if avg_word_length > 7:
            readability -= (avg_word_length - 7) * 5
        if avg_sentence_length > 25:
            readability -= (avg_sentence_length - 25) * 2
        if avg_sentence_length < 8:
            readability -= (8 - avg_sentence_length) * 3
        readability = max(0, min(100, readability))
        
        # 2. Clarity Score (0-100)
        clarity = 100
        if len(grammar_issues) > 0:
            clarity -= len(grammar_issues) * 8
        if 'issues' in structure_analysis.lower():
            clarity -= 15
        if abs(polarity) < 0.1:
            clarity -= 5
        clarity = max(0, min(100, clarity))
        
        # 3. Engagement Score (0-100)
        engagement = 50
        if sentiment == 'Positive':
            engagement += 25
        elif sentiment == 'Negative':
            engagement -= 20
        
        if tone in ['Friendly', 'Formal']:
            engagement += 15
        elif tone == 'Negative':
            engagement -= 25
        
        has_question = '?' in text
        has_call_to_action = any(word in text.lower() for word in ['please', 'kindly', 'would you', 'could you'])
        if has_question:
            engagement += 10
        if has_call_to_action:
            engagement += 10
        
        engagement = max(0, min(100, engagement))
        
        # 4. Professional Impact Score (0-100)
        impact = professionalism_score * 10
        
        if intent in ['Request', 'Meeting Request', 'Inquiry']:
            impact += 10
        if tone == 'Formal':
            impact += 10
        elif tone == 'Negative':
            impact -= 20
        
        if len(words) > 50 and len(words) < 300:
            impact += 5
        elif len(words) < 20:
            impact -= 15
        
        impact = max(0, min(100, impact))
        
        # 5. Overall Quality Score (weighted average)
        overall = (
            readability * 0.20 +
            clarity * 0.30 +
            engagement * 0.20 +
            impact * 0.30
        )
        overall = round(overall)
        
        return {
            "overall_score": overall,
            "readability_score": round(readability),
            "clarity_score": round(clarity),
            "engagement_score": round(engagement),
            "professional_impact_score": round(impact)
        }
