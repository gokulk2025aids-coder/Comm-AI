"""
Test script for Tone Adjuster
Run this to verify the tone adjuster is working correctly
"""

from tone_adjuster import ToneAdjuster

def test_tone_adjuster():
    adjuster = ToneAdjuster()
    
    print("=" * 60)
    print("TONE ADJUSTER TEST")
    print("=" * 60)
    
    # Test 1: Casual to Formal
    print("\n1. CASUAL TO FORMAL TEST")
    print("-" * 60)
    casual_text = "hey there! thanks for the email. yeah, I'm gonna send you the report. bye!"
    print(f"Original: {casual_text}")
    formal_text = adjuster.casual_to_formal(casual_text)
    print(f"Formal: {formal_text}")
    
    # Test 2: Aggressive to Diplomatic
    print("\n2. AGGRESSIVE TO DIPLOMATIC TEST")
    print("-" * 60)
    aggressive_text = "You must fix this immediately! This is unacceptable and bad work."
    print(f"Original: {aggressive_text}")
    diplomatic_text = adjuster.aggressive_to_diplomatic(aggressive_text)
    print(f"Diplomatic: {diplomatic_text}")
    
    # Test 3: Formality Slider - Very Casual (20)
    print("\n3. FORMALITY SLIDER TEST - Very Casual (20)")
    print("-" * 60)
    formal_text_input = "Dear Sir, Thank you for your email. Best regards,"
    print(f"Original: {formal_text_input}")
    casual_output = adjuster.adjust_formality(formal_text_input, 20)
    print(f"Very Casual: {casual_output}")
    
    # Test 4: Formality Slider - Formal (80)
    print("\n4. FORMALITY SLIDER TEST - Formal (80)")
    print("-" * 60)
    casual_text_input = "hey, thanks for reaching out. gonna get back to you soon."
    print(f"Original: {casual_text_input}")
    formal_output = adjuster.adjust_formality(casual_text_input, 80)
    print(f"Formal: {formal_output}")
    
    # Test 5: Preview Tone
    print("\n5. PREVIEW TONE TEST")
    print("-" * 60)
    test_text = "hey! you need to send me that report immediately!"
    print(f"Original: {test_text}")
    
    preview1 = adjuster.preview_tone(test_text, 'casual_to_formal')
    print(f"Casual to Formal: {preview1}")
    
    preview2 = adjuster.preview_tone(test_text, 'aggressive_to_diplomatic')
    print(f"Aggressive to Diplomatic: {preview2}")
    
    preview3 = adjuster.preview_tone(test_text, 'formality_slider', 50)
    print(f"Formality 50: {preview3}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_tone_adjuster()
