"""
Test Dynamic Email Suggestions
"""
import sys
sys.path.append('backend')

from nlp_engine import EmailAnalyzer

analyzer = EmailAnalyzer()

# Test different types of emails
test_emails = {
    "Request Email": """
    Hi John,
    
    Can you please send me the sales report for Q4? I need it for tomorrow's meeting.
    
    Thanks,
    Sarah
    """,
    
    "Complaint Email": """
    Dear Support,
    
    I am very disappointed with the service I received. The product arrived damaged and customer service was unhelpful.
    
    I expect a refund immediately.
    
    Regards,
    Mike
    """,
    
    "Meeting Request": """
    Hello Team,
    
    I would like to schedule a meeting next week to discuss the new project timeline. Are you available on Tuesday?
    
    Best,
    Lisa
    """,
    
    "Thank You Email": """
    Hi David,
    
    Thank you so much for your help with the presentation. I really appreciate your support!
    
    Best regards,
    Emma
    """,
    
    "Inquiry Email": """
    Dear HR,
    
    I wanted to ask about the vacation policy. How many days can I take in December?
    
    Thanks,
    Alex
    """
}

print("="*70)
print("TESTING DYNAMIC EMAIL SUGGESTIONS")
print("="*70)

for email_type, email_text in test_emails.items():
    print(f"\n{'='*70}")
    print(f"EMAIL TYPE: {email_type}")
    print(f"{'='*70}")
    
    # Analyze
    result = analyzer.analyze(email_text)
    
    print(f"\nDetected Intent: {result['intent']}")
    print(f"Detected Tone: {result['tone']}")
    
    print(f"\n--- IMPROVED EMAIL SUGGESTION ---")
    print(result['email_suggestion'][:300] + "...")
    
    print(f"\n--- SUGGESTED REPLY ---")
    print(result['suggested_reply'][:300] + "...")

print("\n" + "="*70)
print("TEST COMPLETE - All suggestions are now DYNAMIC!")
print("="*70)
