from fpdf import FPDF
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ReportPDFGenerator:
    def __init__(self):
        self.colors = {
            'primary': (102, 126, 234),
            'success': (34, 197, 94),
            'warning': (234, 179, 8),
            'danger': (239, 68, 68),
            'dark': (31, 41, 55),
            'light': (243, 244, 246)
        }
    
    def _clean_text(self, text):
        """Remove emojis and special Unicode characters that aren't supported by Arial font"""
        if not text:
            return text
        
        # Remove common emojis and replace with ASCII equivalents
        emoji_map = {
            '🌟': '*', '⭐': '*', '✨': '*',
            '📈': '^', '📊': '#', '📉': 'v',
            '✓': 'v', '✔': 'v', '✅': '[OK]',
            '✗': 'x', '✘': 'x', '❌': '[X]',
            '⚠': '!', '⚠️': '!',
            '💡': '*', '🎯': '*', '📝': '*',
            '👍': '+', '👎': '-',
            '🔥': '*', '💪': '+', '🎉': '*',
            '📧': '[Email]', '📬': '[Mail]',
            '🚀': '^', '⬆': '^', '⬇': 'v',
            '➡': '>', '⬅': '<',
            '•': '-', '◆': '*', '▪': '-'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        
        # Remove any remaining non-ASCII characters
        text = ''.join(char if ord(char) < 128 else '' for char in text)
        
        return text
    
    def generate_report_pdf(self, report_data, user_email):
        """Generate PDF report from report data"""
        try:
            logger.info("Starting PDF generation...")
            logger.info(f"Report data keys: {list(report_data.keys()) if report_data else 'None'}")
            logger.info(f"User email: {user_email}")
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            logger.info("Adding header...")
            # Header
            self._add_header(pdf, report_data, user_email)
            
            logger.info("Adding summary section...")
            # Summary Section
            if 'summary' in report_data and report_data['summary']:
                self._add_summary_section(pdf, report_data['summary'])
            else:
                logger.warning("No summary data found")
            
            logger.info("Adding improvements section...")
            # Most Improved Areas
            if 'most_improved_areas' in report_data:
                self._add_improvements_section(pdf, report_data['most_improved_areas'])
            else:
                logger.warning("No improvements data found")
            
            logger.info("Adding needs work section...")
            # Areas Needing Work
            if 'areas_needing_work' in report_data:
                self._add_needs_work_section(pdf, report_data['areas_needing_work'])
            else:
                logger.warning("No needs work data found")
            
            logger.info("Adding trends section...")
            # Writing Trends
            if 'writing_trends' in report_data and report_data['writing_trends']:
                self._add_trends_section(pdf, report_data['writing_trends'])
            else:
                logger.warning("No trends data found")
            
            logger.info("Adding insights section...")
            # Insights
            if 'insights' in report_data:
                self._add_insights_section(pdf, report_data['insights'])
            else:
                logger.warning("No insights data found")
            
            logger.info("Adding footer...")
            # Footer
            self._add_footer(pdf)
            
            logger.info("Generating PDF bytes...")
            # Return PDF as bytes - using the correct method for fpdf2
            pdf_bytes = bytes(pdf.output())
            logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"Error generating report PDF: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _add_header(self, pdf, report_data, user_email):
        """Add report header"""
        try:
            # Logo/Title
            pdf.set_font('Arial', 'B', 24)
            pdf.set_text_color(*self.colors['primary'])
            pdf.cell(0, 15, 'CommAI Email Analysis Report', 0, 1, 'C')
            
            # Period and user info
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(*self.colors['dark'])
            
            period_label = report_data.get('period_label', 'Report')
            pdf.cell(0, 8, f"Period: {period_label}", 0, 1, 'C')
            pdf.cell(0, 8, f"Generated for: {user_email}", 0, 1, 'C')
            pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 0, 1, 'C')
            
            pdf.ln(10)
            
            # Divider
            pdf.set_draw_color(*self.colors['primary'])
            pdf.set_line_width(0.5)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(10)
        except Exception as e:
            logger.error(f"Error in _add_header: {e}")
            raise
    
    def _add_summary_section(self, pdf, summary):
        """Add summary statistics section"""
        # Section title
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*self.colors['primary'])
        pdf.cell(0, 10, 'Summary Statistics', 0, 1)
        pdf.ln(3)
        
        # Summary box
        pdf.set_fill_color(*self.colors['light'])
        pdf.rect(20, pdf.get_y(), 170, 70, 'F')
        
        y_start = pdf.get_y() + 5
        
        # Total emails
        pdf.set_xy(25, y_start)
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*self.colors['dark'])
        pdf.cell(80, 8, 'Total Emails Analyzed:', 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, str(summary['total_emails_analyzed']), 0, 1)
        
        # Scores
        scores = [
            ('Average Professionalism:', f"{summary['average_professionalism']}/10", summary['average_professionalism']),
            ('Average Overall Quality:', f"{summary['average_overall_quality']}/100", summary['average_overall_quality']),
            ('Average Readability:', f"{summary['average_readability']}/100", summary['average_readability']),
            ('Average Clarity:', f"{summary['average_clarity']}/100", summary['average_clarity']),
            ('Average Engagement:', f"{summary['average_engagement']}/100", summary['average_engagement']),
            ('Average Grammar Issues:', str(summary['average_grammar_issues']), None)
        ]
        
        for label, value, score in scores:
            pdf.set_x(25)
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(*self.colors['dark'])
            pdf.cell(80, 7, label, 0, 0)
            pdf.set_font('Arial', '', 11)
            
            # Color code based on score
            if score is not None:
                if score >= 80 or (label.startswith('Average Professionalism') and score >= 8):
                    pdf.set_text_color(*self.colors['success'])
                elif score >= 60 or (label.startswith('Average Professionalism') and score >= 6):
                    pdf.set_text_color(*self.colors['primary'])
                elif score >= 40 or (label.startswith('Average Professionalism') and score >= 4):
                    pdf.set_text_color(*self.colors['warning'])
                else:
                    pdf.set_text_color(*self.colors['danger'])
            else:
                pdf.set_text_color(*self.colors['dark'])
            
            pdf.cell(0, 7, value, 0, 1)
        
        pdf.ln(10)
    
    def _add_improvements_section(self, pdf, improvements):
        """Add most improved areas section"""
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*self.colors['success'])
        pdf.cell(0, 10, 'Most Improved Areas', 0, 1)
        pdf.ln(3)
        
        if not improvements or len(improvements) == 0:
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 7, '  No improvements detected yet. Keep analyzing emails!', 0, 1)
            pdf.ln(5)
            return
        
        for item in improvements:
            # Area name
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(*self.colors['dark'])
            area_text = self._clean_text(str(item.get('area', '')))
            pdf.cell(0, 8, f"[+] {area_text}", 0, 1)
            
            # Details
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(80, 80, 80)
            
            if 'improvement' in item and item['improvement']:
                improvement_text = self._clean_text(str(item['improvement']))
                pdf.cell(0, 6, f"   Improvement: {improvement_text}", 0, 1)
            if 'achievement' in item and item['achievement']:
                achievement_text = self._clean_text(str(item['achievement']))
                pdf.cell(0, 6, f"   Achievement: {achievement_text}", 0, 1)
            if 'score' in item and item['score']:
                pdf.cell(0, 6, f"   Score: {str(item['score'])}", 0, 1)
            if 'description' in item and item['description']:
                desc_text = self._clean_text(str(item['description'])[:100])
                pdf.cell(0, 6, f"   {desc_text}", 0, 1)
            
            pdf.ln(3)
        
        pdf.ln(5)
    
    def _add_needs_work_section(self, pdf, needs_work):
        """Add areas needing work section"""
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*self.colors['warning'])
        pdf.cell(0, 10, 'Areas Needing Work', 0, 1)
        pdf.ln(3)
        
        if not needs_work or len(needs_work) == 0:
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 7, '  Great job! No major areas of concern.', 0, 1)
            pdf.ln(5)
            return
        
        for item in needs_work:
            # Area name
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(*self.colors['dark'])
            area_text = self._clean_text(str(item.get('area', '')))
            pdf.cell(0, 8, f"[!] {area_text}", 0, 1)
            
            # Details
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(80, 80, 80)
            
            if 'decline' in item and item['decline']:
                decline_text = self._clean_text(str(item['decline']))
                pdf.cell(0, 6, f"   Decline: {decline_text}", 0, 1)
            if 'issue' in item and item['issue']:
                issue_text = self._clean_text(str(item['issue']))
                pdf.cell(0, 6, f"   Issue: {issue_text}", 0, 1)
            if 'score' in item and item['score']:
                pdf.cell(0, 6, f"   Score: {str(item['score'])}", 0, 1)
            if 'description' in item and item['description']:
                desc_text = self._clean_text(str(item['description'])[:100])
                pdf.cell(0, 6, f"   {desc_text}", 0, 1)
            
            pdf.ln(3)
        
        pdf.ln(5)
    
    def _add_trends_section(self, pdf, trends):
        """Add writing trends section"""
        try:
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(*self.colors['primary'])
            pdf.cell(0, 10, 'Writing Trends', 0, 1)
            pdf.ln(3)
            
            # Trend items with safe access
            trend_items = []
            
            if 'professionalism_trend' in trends and trends['professionalism_trend']:
                pt = trends['professionalism_trend']
                direction = pt.get('direction', 'stable').title()
                change = pt.get('change', 0)
                trend_items.append(('Professionalism Trend:', f"{direction} ({change:+.1f})"))
            
            if 'overall_quality_trend' in trends and trends['overall_quality_trend']:
                oqt = trends['overall_quality_trend']
                direction = oqt.get('direction', 'stable').title()
                change = oqt.get('change', 0)
                trend_items.append(('Overall Quality Trend:', f"{direction} ({change:+.1f})"))
            
            trend_items.extend([
                ('Most Used Tone:', trends.get('most_used_tone', 'N/A')),
                ('Most Common Intent:', trends.get('most_common_intent', 'N/A')),
                ('Dominant Sentiment:', trends.get('dominant_sentiment', 'N/A')),
                ('Typical Priority:', trends.get('typical_priority', 'N/A'))
            ])
            
            for label, value in trend_items:
                pdf.set_font('Arial', 'B', 11)
                pdf.set_text_color(*self.colors['dark'])
                pdf.cell(70, 7, label, 0, 0)
                pdf.set_font('Arial', '', 11)
                pdf.set_text_color(80, 80, 80)
                pdf.cell(0, 7, str(value), 0, 1)
            
            pdf.ln(8)
        except Exception as e:
            logger.error(f"Error in _add_trends_section: {e}")
            # Add a simple fallback
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 7, '  Trends data unavailable', 0, 1)
            pdf.ln(5)
    
    def _add_insights_section(self, pdf, insights):
        """Add insights section"""
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*self.colors['primary'])
        pdf.cell(0, 10, 'Key Insights', 0, 1)
        pdf.ln(3)
        
        if not insights or len(insights) == 0:
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 7, '  Continue analyzing emails to generate insights.', 0, 1)
            pdf.ln(5)
            return
        
        for insight in insights:
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(*self.colors['dark'])
            # Limit insight length and clean text
            insight_text = str(insight)[:120] if len(str(insight)) > 120 else str(insight)
            insight_text = self._clean_text(insight_text)
            if insight_text.strip():  # Only add if not empty
                pdf.cell(0, 7, f"  - {insight_text}", 0, 1)
                pdf.ln(2)
        
        pdf.ln(5)
    
    def _add_footer(self, pdf):
        """Add report footer"""
        pdf.ln(10)
        pdf.set_draw_color(*self.colors['primary'])
        pdf.set_line_width(0.5)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 5, 'Generated by CommAI - Advanced Email Analysis Platform', 0, 1, 'C')
        pdf.cell(0, 5, 'Continue analyzing emails to track your progress over time', 0, 1, 'C')
