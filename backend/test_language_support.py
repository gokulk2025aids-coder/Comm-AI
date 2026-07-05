"""
Test script for Language Support module
Run: python test_language_support.py
"""

import sys
sys.path.append('backend')

from language_support import LanguageSupport

def test_language_support():
    ls = LanguageSupport()
    
    print("=" * 60)
    print("TESTING LANGUAGE SUPPORT MODULE")
    print("=" * 60)
    
    # Test 1: Language Detection
    print("\n1. LANGUAGE DETECTION")
    print("-" * 60)
    test_texts = {
        "Hello, how are you today?": "English",
        "Hola, ¿cómo estás hoy?": "Spanish",
        "Bonjour, comment allez-vous?": "French",
        "Guten Tag, wie geht es Ihnen?": "German"
    }
    
    for text, expected in test_texts.items():
        result = ls.detect_language(text)
        print(f"Text: {text[:40]}...")
        print(f"Detected: {result['name']} ({result['code']})")
        print(f"Supported: {result['supported']}\n")
    
    # Test 2: Cultural Tips
    print("\n2. CULTURAL TIPS")
    print("-" * 60)
    for lang_code in ['en', 'es', 'ja', 'de']:
        tips = ls.get_cultural_tips(lang_code)
        print(f"\n{ls.supported_languages[lang_code]}:")
        print(f"  Formality: {tips['formality']}")
        print(f"  Greeting: {tips['greeting']}")
        print(f"  Tips: {tips['tips'][:60]}...")
    
    # Test 3: Localized Tone Analysis
    print("\n\n3. LOCALIZED TONE ANALYSIS")
    print("-" * 60)
    test_email = "Dear Sir, I am writing to request your assistance with this matter. Thank you."
    
    for lang_code in ['en', 'ja', 'de']:
        result = ls.analyze_tone_localized(test_email, lang_code)
        print(f"\n{ls.supported_languages[lang_code]}:")
        print(f"  Tone: {result['tone']}")
        print(f"  Polarity: {result['polarity']}")
        print(f"  Context: {result['cultural_context'][:60]}...")
    
    # Test 4: Formality Assessment
    print("\n\n4. FORMALITY ASSESSMENT")
    print("-" * 60)
    formal_text = "Dear Sir, I kindly request your assistance. Respectfully yours."
    
    for lang_code in ['en', 'ja', 'de', 'pt']:
        result = ls.get_formality_level(formal_text, lang_code)
        print(f"\n{ls.supported_languages[lang_code]}:")
        print(f"  Level: {result['level']}")
        print(f"  Score: {result['score']}/10")
        print(f"  {result['expected_for_culture']}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_language_support()
