"""
Test script to verify PDF generation works correctly
Run this to test if the PDF generator is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from report_pdf_generator import ReportPDFGenerator

# Sample report data
test_report_data = {
    'period_label': 'Weekly Report (Dec 15-22, 2024)',
    'summary': {
        'total_emails_analyzed': 5,
        'average_professionalism': 7.5,
        'average_overall_quality': 75,
        'average_readability': 80,
        'average_clarity': 78,
        'average_engagement': 72,
        'average_grammar_issues': 2
    },
    'most_improved_areas': [
        {
            'area': 'Professionalism',
            'improvement': 'Score increased by 15%',
            'achievement': 'Maintained formal tone',
            'score': '8/10',
            'description': 'Great progress in professional communication'
        }
    ],
    'areas_needing_work': [
        {
            'area': 'Grammar',
            'decline': 'More errors detected',
            'issue': 'Spelling mistakes increased',
            'score': '6/10',
            'description': 'Need to focus on proofreading'
        }
    ],
    'writing_trends': {
        'professionalism_trend': {'direction': 'improving', 'change': 1.5},
        'overall_quality_trend': {'direction': 'stable', 'change': 0.2},
        'most_used_tone': 'Formal',
        'most_common_intent': 'Request',
        'dominant_sentiment': 'Positive',
        'typical_priority': 'Medium'
    },
    'insights': [
        'Your professionalism score has improved significantly',
        'Consider focusing more on grammar and spelling',
        'Your email clarity is excellent - keep it up!'
    ]
}

def test_pdf_generation():
    print("Testing PDF generation...")
    
    try:
        generator = ReportPDFGenerator()
        pdf_bytes = generator.generate_report_pdf(test_report_data, 'test@example.com')
        
        print(f"✅ PDF generated successfully!")
        print(f"   Size: {len(pdf_bytes)} bytes")
        print(f"   Type: {type(pdf_bytes)}")
        
        # Save to file for testing
        with open('test_report.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"✅ PDF saved to test_report.pdf")
        print(f"   Try opening it to verify it works!")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF generation failed!")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
