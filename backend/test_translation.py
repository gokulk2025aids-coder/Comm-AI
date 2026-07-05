"""
Test Translation Functionality
"""
import sys
sys.path.append('backend')

from language_support import LanguageSupport

ls = LanguageSupport()

# Test translations
tests = {
    "Chinese": "尊敬的王先生，感谢您的来信。我们将在下周完成项目报告。",
    "Spanish": "Estimado Sr. García, espero que este correo le encuentre bien.",
    "French": "Bonjour, comment allez-vous aujourd'hui?",
    "Japanese": "お世話になっております。来週の会議について確認させていただきます。",
    "German": "Sehr geehrte Damen und Herren, vielen Dank für Ihre E-Mail.",
}

print("="*60)
print("TRANSLATION TEST")
print("="*60)

for lang_name, text in tests.items():
    print(f"\n{lang_name}:")
    print(f"Original length: {len(text)} characters")
    
    # Detect language
    detected = ls.detect_language(text)
    print(f"Detected: {detected['name']} ({detected['code']})")
    
    # Translate to English
    translated = ls.translate_text(text, 'en')
    
    if "Translation Service Unavailable" in translated:
        print("Status: FAILED")
    else:
        print("Status: SUCCESS")
        print(f"Translated length: {len(translated)} characters")

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
