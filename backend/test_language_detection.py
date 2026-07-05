"""
Quick test for language detection
"""
import sys
sys.path.append('backend')

from language_support import LanguageSupport

ls = LanguageSupport()

# Test different languages
tests = {
    "English": "Hello, how are you today? I hope this email finds you well.",
    "Spanish": "Hola, ¿cómo estás hoy? Espero que este correo te encuentre bien.",
    "French": "Bonjour, comment allez-vous aujourd'hui? J'espère que ce courriel vous trouve bien.",
    "German": "Hallo, wie geht es dir heute? Ich hoffe, diese E-Mail findet Sie gut.",
    "Japanese": "こんにちは、今日はお元気ですか？このメールがあなたを元気に見つけることを願っています。",
    "Chinese": "你好，你今天好吗？我希望这封邮件能让你感觉良好。",
    "Arabic": "مرحبا، كيف حالك اليوم؟ أتمنى أن يجدك هذا البريد الإلكتروني بخير.",
    "Hindi": "नमस्ते, आज आप कैसे हैं? मुझे उम्मीद है कि यह ईमेल आपको अच्छा लगेगा।",
    "Portuguese": "Olá, como você está hoje? Espero que este e-mail o encontre bem.",
    "Russian": "Здравствуйте, как вы сегодня? Надеюсь, это письмо найдет вас хорошо.",
}

print("="*60)
print("LANGUAGE DETECTION TEST")
print("="*60)

for expected_lang, text in tests.items():
    result = ls.detect_language(text)
    status = "OK" if result['supported'] else "X"
    print(f"\n{status} Expected: {expected_lang}")
    print(f"  Detected: {result['name']} ({result['code']})")
    print(f"  Confidence: {result.get('confidence', 0)}%")
    print(f"  Supported: {result['supported']}")

print("\n" + "="*60)
print("TEST COMPLETE!")
print("="*60)
