import re
from textblob import TextBlob

class SubjectLineAnalyzer:
    def __init__(self):
        # Power words that increase open rates
        self.power_words = {
            'urgency': ['urgent', 'asap', 'now', 'today', 'deadline', 'limited', 'hurry', 'quick', 'fast', 'immediate'],
            'curiosity': ['secret', 'revealed', 'discover', 'hidden', 'exclusive', 'insider', 'behind', 'truth', 'mystery'],
            'value': ['free', 'save', 'discount', 'bonus', 'gift', 'offer', 'deal', 'special', 'new', 'improved'],
            'personal': ['you', 'your', 'personalized', 'custom', 'invitation', 'selected', 'exclusive'],
            'action': ['get', 'download', 'claim', 'join', 'register', 'start', 'try', 'learn', 'discover']
        }
        
        # Spam trigger words
        self.spam_words = ['free', 'winner', 'cash', 'prize', 'guarantee', 'no obligation', 'act now', 
                          'click here', 'buy now', 'order now', 'limited time', '100%', 'risk-free',
                          'money back', 'credit card', 'viagra', 'weight loss', 'earn money']
        
        # Optimal length ranges
        self.optimal_min = 30
        self.optimal_max = 60
    
    def analyze_subject_line(self, subject):
        """Comprehensive analysis of email subject line"""
        if not subject or not subject.strip():
            return {
                "error": "Subject line cannot be empty",
                "score": 0
            }
        
        subject = subject.strip()
        
        # Basic metrics
        char_count = len(subject)
        word_count = len(subject.split())
        
        # Sentiment analysis
        blob = TextBlob(subject)
        sentiment = blob.sentiment.polarity
        
        # Check for power words
        power_word_categories = []
        power_word_count = 0
        subject_lower = subject.lower()
        
        for category, words in self.power_words.items():
            found_words = [word for word in words if word in subject_lower]
            if found_words:
                power_word_categories.append(category)
                power_word_count += len(found_words)
        
        # Check for spam words
        spam_word_list = [word for word in self.spam_words if word in subject_lower]
        spam_score = len(spam_word_list)
        
        # Check for special characters
        has_emoji = bool(re.search(r'[^\w\s,.-]', subject))
        has_numbers = bool(re.search(r'\d', subject))
        has_question = '?' in subject
        has_exclamation = '!' in subject
        excessive_punctuation = subject.count('!') > 1 or subject.count('?') > 1
        all_caps = subject.isupper() and len(subject) > 5
        
        # Personalization check
        has_personalization = any(word in subject_lower for word in ['you', 'your', 'personalized'])
        
        # Calculate effectiveness score (0-100)
        score = 50  # Base score
        
        # Length scoring
        if self.optimal_min <= char_count <= self.optimal_max:
            score += 15
        elif char_count < self.optimal_min:
            score -= 10
        elif char_count > self.optimal_max:
            score -= 15
        
        # Power words bonus
        score += min(power_word_count * 5, 20)
        
        # Spam penalty
        score -= spam_score * 10
        
        # Sentiment bonus
        if 0.1 <= sentiment <= 0.5:
            score += 10
        elif sentiment > 0.5:
            score += 5
        
        # Special features
        if has_personalization:
            score += 10
        if has_numbers:
            score += 5
        if has_question:
            score += 5
        if has_emoji and not excessive_punctuation:
            score += 5
        
        # Penalties
        if all_caps:
            score -= 20
        if excessive_punctuation:
            score -= 15
        if spam_score > 0:
            score -= 20
        
        # Clamp score between 0-100
        score = max(0, min(100, score))
        
        # Determine grade
        if score >= 80:
            grade = 'A'
            grade_text = 'Excellent'
        elif score >= 70:
            grade = 'B'
            grade_text = 'Good'
        elif score >= 60:
            grade = 'C'
            grade_text = 'Average'
        elif score >= 50:
            grade = 'D'
            grade_text = 'Below Average'
        else:
            grade = 'F'
            grade_text = 'Poor'
        
        # Predict open rate
        open_rate = self._predict_open_rate(score, power_word_count, has_personalization, char_count)
        
        # Generate insights
        insights = self._generate_insights(
            char_count, word_count, power_word_categories, spam_word_list,
            has_personalization, has_numbers, has_question, all_caps,
            excessive_punctuation, sentiment
        )
        
        return {
            "subject": subject,
            "score": round(score),
            "grade": grade,
            "grade_text": grade_text,
            "char_count": char_count,
            "word_count": word_count,
            "optimal_length": f"{self.optimal_min}-{self.optimal_max} characters",
            "sentiment": "Positive" if sentiment > 0.1 else "Negative" if sentiment < -0.1 else "Neutral",
            "sentiment_score": round(sentiment, 2),
            "power_words": power_word_categories,
            "power_word_count": power_word_count,
            "spam_words": spam_word_list,
            "spam_risk": "High" if spam_score > 2 else "Medium" if spam_score > 0 else "Low",
            "has_personalization": has_personalization,
            "has_numbers": has_numbers,
            "has_question": has_question,
            "has_emoji": has_emoji,
            "all_caps": all_caps,
            "excessive_punctuation": excessive_punctuation,
            "predicted_open_rate": open_rate,
            "insights": insights
        }
    
    def _predict_open_rate(self, score, power_word_count, has_personalization, char_count):
        """Predict email open rate based on subject line quality"""
        # Base rate from score
        base_rate = 10 + (score * 0.3)  # 10-40% base
        
        # Adjustments
        if power_word_count > 0:
            base_rate += 5
        if has_personalization:
            base_rate += 8
        if self.optimal_min <= char_count <= self.optimal_max:
            base_rate += 5
        
        # Clamp between 5-60%
        open_rate = max(5, min(60, base_rate))
        
        return {
            "min": round(open_rate - 5, 1),
            "max": round(open_rate + 5, 1),
            "average": round(open_rate, 1)
        }
    
    def _generate_insights(self, char_count, word_count, power_words, spam_words,
                          has_personalization, has_numbers, has_question, all_caps,
                          excessive_punctuation, sentiment):
        """Generate actionable insights"""
        insights = []
        
        # Length insights
        if char_count < self.optimal_min:
            insights.append({
                "type": "warning",
                "category": "Length",
                "message": f"Subject line is too short ({char_count} chars). Aim for {self.optimal_min}-{self.optimal_max} characters.",
                "impact": "Medium"
            })
        elif char_count > self.optimal_max:
            insights.append({
                "type": "warning",
                "category": "Length",
                "message": f"Subject line is too long ({char_count} chars). It may get cut off on mobile devices.",
                "impact": "High"
            })
        else:
            insights.append({
                "type": "success",
                "category": "Length",
                "message": f"Perfect length! ({char_count} characters)",
                "impact": "Positive"
            })
        
        # Power words
        if power_words:
            insights.append({
                "type": "success",
                "category": "Engagement",
                "message": f"Contains power words: {', '.join(power_words)}. This increases engagement!",
                "impact": "Positive"
            })
        else:
            insights.append({
                "type": "info",
                "category": "Engagement",
                "message": "Consider adding power words (urgency, curiosity, value) to increase open rates.",
                "impact": "Medium"
            })
        
        # Personalization
        if has_personalization:
            insights.append({
                "type": "success",
                "category": "Personalization",
                "message": "Includes personalization! This can increase open rates by 26%.",
                "impact": "Positive"
            })
        else:
            insights.append({
                "type": "info",
                "category": "Personalization",
                "message": "Add personalization (e.g., 'Your', 'You') to make it more engaging.",
                "impact": "Medium"
            })
        
        # Numbers
        if has_numbers:
            insights.append({
                "type": "success",
                "category": "Specificity",
                "message": "Contains numbers! Specific numbers increase credibility and open rates.",
                "impact": "Positive"
            })
        
        # Question
        if has_question:
            insights.append({
                "type": "success",
                "category": "Curiosity",
                "message": "Question format creates curiosity and engagement!",
                "impact": "Positive"
            })
        
        # Spam warnings
        if spam_words:
            insights.append({
                "type": "danger",
                "category": "Spam Risk",
                "message": f"Contains spam trigger words: {', '.join(spam_words[:3])}. May end up in spam folder!",
                "impact": "High"
            })
        
        # All caps warning
        if all_caps:
            insights.append({
                "type": "danger",
                "category": "Formatting",
                "message": "ALL CAPS appears aggressive and spammy. Use normal capitalization.",
                "impact": "High"
            })
        
        # Excessive punctuation
        if excessive_punctuation:
            insights.append({
                "type": "warning",
                "category": "Formatting",
                "message": "Too many exclamation/question marks. Use sparingly for better impact.",
                "impact": "Medium"
            })
        
        # Sentiment
        if sentiment < -0.2:
            insights.append({
                "type": "warning",
                "category": "Tone",
                "message": "Negative tone detected. Consider more positive or neutral language.",
                "impact": "Medium"
            })
        
        return insights
    
    def suggest_improvements(self, subject):
        """Generate improved subject line suggestions"""
        analysis = self.analyze_subject_line(subject)
        
        if "error" in analysis:
            return {"error": analysis["error"]}
        
        suggestions = []
        
        # Original with improvements
        improved = subject.strip()
        
        # Fix all caps
        if analysis['all_caps']:
            improved = improved.title()
        
        # Remove excessive punctuation
        improved = re.sub(r'!{2,}', '!', improved)
        improved = re.sub(r'\?{2,}', '?', improved)
        
        # Base suggestion
        suggestions.append({
            "subject": improved,
            "reason": "Cleaned up formatting",
            "expected_improvement": "+5-10% open rate"
        })
        
        # Add personalization if missing
        if not analysis['has_personalization']:
            personalized = f"Your {improved}" if not improved.lower().startswith('your') else improved
            suggestions.append({
                "subject": personalized,
                "reason": "Added personalization",
                "expected_improvement": "+15-25% open rate"
            })
        
        # Add numbers if missing
        if not analysis['has_numbers']:
            with_number = f"5 Ways: {improved}" if len(improved) < 50 else improved
            suggestions.append({
                "subject": with_number,
                "reason": "Added specific number for credibility",
                "expected_improvement": "+10-15% open rate"
            })
        
        # Add curiosity if no question
        if not analysis['has_question'] and len(improved) < 50:
            curious = f"{improved}?"
            suggestions.append({
                "subject": curious,
                "reason": "Added question to create curiosity",
                "expected_improvement": "+8-12% open rate"
            })
        
        # Shorten if too long
        if analysis['char_count'] > self.optimal_max:
            words = improved.split()
            shortened = ' '.join(words[:6]) + '...'
            suggestions.append({
                "subject": shortened,
                "reason": "Shortened for mobile devices",
                "expected_improvement": "+10-15% open rate"
            })
        
        return {
            "original": subject,
            "original_score": analysis['score'],
            "suggestions": suggestions[:5]  # Top 5 suggestions
        }
    
    def generate_ab_tests(self, subject):
        """Generate A/B testing variations"""
        analysis = self.analyze_subject_line(subject)
        
        if "error" in analysis:
            return {"error": analysis["error"]}
        
        variations = []
        
        # Variation 1: With urgency
        urgent = f"⏰ {subject}" if not any(word in subject.lower() for word in self.power_words['urgency']) else subject
        variations.append({
            "version": "A",
            "subject": subject,
            "strategy": "Original (Control)",
            "focus": "Baseline performance"
        })
        
        # Variation 2: With personalization
        personal = f"Your {subject}" if not subject.lower().startswith('your') else f"{subject} - Just for You"
        variations.append({
            "version": "B",
            "subject": personal,
            "strategy": "Personalization",
            "focus": "Test personal connection"
        })
        
        # Variation 3: With numbers
        numbered = f"5 Tips: {subject}" if not re.search(r'\d', subject) else subject
        variations.append({
            "version": "C",
            "subject": numbered,
            "strategy": "Specificity (Numbers)",
            "focus": "Test credibility boost"
        })
        
        # Variation 4: Question format
        question = f"{subject}?" if '?' not in subject else f"How to: {subject}"
        variations.append({
            "version": "D",
            "subject": question,
            "strategy": "Curiosity (Question)",
            "focus": "Test engagement"
        })
        
        # Variation 5: Emoji
        emoji = f"✨ {subject}" if not re.search(r'[^\w\s,.-]', subject) else subject
        variations.append({
            "version": "E",
            "subject": emoji,
            "strategy": "Visual Appeal (Emoji)",
            "focus": "Test attention-grabbing"
        })
        
        return {
            "original": subject,
            "test_plan": {
                "recommended_sample_size": "Minimum 1,000 recipients per variation",
                "duration": "Send all variations simultaneously",
                "success_metric": "Open rate (primary), Click rate (secondary)",
                "statistical_significance": "Wait for 95% confidence level"
            },
            "variations": variations
        }
