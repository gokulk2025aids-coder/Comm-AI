"""
Test Multi-Language Email Analysis
Run this to test emails in different languages
"""

import sys
sys.path.append('backend')

from multilanguage_support import MultiLanguageSupport

# Initialize
ml = MultiLanguageSupport()

# Test emails in different languages
test_emails = {
    "Spanish": """
    Estimado Sr. García,
    
    Espero que este correo le encuentre bien. Le escribo para solicitar una reunión 
    la próxima semana para discutir el proyecto. ¿Estaría disponible el martes?
    
    Atentamente,
    Juan
    """,
    
    "French": """
    Madame, Monsieur,
    
    Je vous écris pour vous informer que le rapport sera prêt demain. 
    Merci de votre patience et compréhension.
    
    Cordialement,
    Marie
    """,
    
    "German": """
    Sehr geehrte Damen und Herren,
    
    Vielen Dank für Ihre E-Mail. Ich werde die Dokumente bis Freitag fertigstellen.
    
    Mit freundlichen Grüßen,
    Hans
    """,
    
    "Japanese": """
    お世話になっております。
    
    来週の会議について確認させていただきたく、ご連絡いたしました。
    ご都合はいかがでしょうか。
    
    よろしくお願いいたします。
    """,
    
    "Chinese": """
    尊敬的王先生，
    
    感谢您的来信。我们将在下周完成项目报告。
    如有任何问题，请随时联系我。
    
    此致
    敬礼
    """,
    
    "Arabic": """
    السلام عليكم ورحمة الله وبركاته
    
    أتمنى أن تكون بخير. أكتب إليك بخصوص الاجتماع القادم.
    
    مع أطيب التحيات
    """
}

print("=" * 60)
print("MULTI-LANGUAGE EMAIL ANALYSIS TEST")
print("=" * 60)

for lang_name, email_text in test_emails.items():
    print(f"\n{'='*60}")
    print(f"Testing: {lang_name}")
    print(f"{'='*60}")
    
    # Detect language
    detection = ml.detect_language(email_text)
    print(f"\n✓ Detected: {detection['language_name']} ({detection['language_code']})")
    print(f"  Confidence: {detection['confidence']}%")
    
    # Get cultural tips
    if detection['supported']:
        tips = ml.get_cultural_tips(detection['language_code'])
        print(f"\n✓ Cultural Tips:")
        print(f"  Formality: {tips['formality_level']}")
        print(f"  Greeting: {tips['greeting_style']}")
        print(f"  Directness: {tips['directness']}")
        
        # Translate to English
        if detection['language_code'] != 'en':
            translation = ml.translate_text(email_text, target_lang='en')
            if translation['success']:
                print(f"\n✓ Translation to English:")
                print(f"  {translation['translated_text'][:100]}...")
    
    print()

print("\n" + "="*60)
print("SUPPORTED LANGUAGES:")
print("="*60)
languages = ml.get_supported_languages()
for lang in languages[:10]:  # Show first 10
    print(f"  • {lang['name']} ({lang['code']})")
print(f"  ... and {len(languages) - 10} more!")
