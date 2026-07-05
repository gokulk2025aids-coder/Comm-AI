from fpdf import FPDF
from datetime import datetime
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

class PDFGenerator:
    def __init__(self):
        self.pdf = None
    
    def generate_report(self, analysis, email_text, user_email=None, theme='dark'):
        try:
            self.pdf = FPDF()
            self.pdf.add_page()
            self.pdf.set_auto_page_break(auto=True, margin=30)  # Increased margin for footer
            
            # Store user email and theme for footer
            self._user_email = user_email
            self._theme = theme
            
            # Clean email text to remove problematic characters
            email_text = self._clean_text(email_text)
            
            # Clean analysis data
            analysis = self._clean_analysis_data(analysis)
            
            # Set colors based on theme
            if theme == 'light':
                self.bg_color = (255, 255, 255)
                self.text_color = (31, 41, 55)
                self.header_bg = (99, 102, 241)
                self.card_bg = (249, 250, 251)
                self.box_colors = {
                    'email': (240, 242, 255),
                    'summary': (255, 247, 237),
                    'reply': (220, 252, 231)
                }
            else:  # dark
                self.bg_color = (20, 20, 30)  # Very dark background
                self.text_color = (240, 240, 245)  # Light text
                self.header_bg = (99, 102, 241)
                self.card_bg = (30, 30, 45)  # Dark card background
                self.box_colors = {
                    'email': (35, 35, 50),
                    'summary': (40, 35, 50),
                    'reply': (30, 45, 40)
                }
            
            # Set page background
            self.pdf.set_fill_color(*self.bg_color)
            self.pdf.rect(0, 0, 210, 297, 'F')
            
            # Header with gradient effect (simulated with colored rectangle)
            self.pdf.set_fill_color(*self.header_bg)
            self.pdf.rect(0, 0, 210, 40, 'F')
            
            # Title
            self.pdf.set_font('Arial', 'B', 24)
            self.pdf.set_text_color(255, 255, 255)
            self.pdf.set_xy(10, 12)
            self.pdf.cell(0, 10, 'Email Analysis Report', ln=True, align='C')
            
            # Subtitle
            self.pdf.set_font('Arial', '', 11)
            self.pdf.set_xy(10, 25)
            self.pdf.cell(0, 8, f'Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', ln=True, align='C')
            
            self.pdf.set_y(45)
            self.pdf.set_text_color(*self.text_color)
            
            # Quick Stats Box
            self._add_stats_box(analysis)
            
            # Original Email Section
            self._add_section_header('Original Email', '')
            self._add_box_content(email_text[:600] + ('...' if len(email_text) > 600 else ''), 'email')
            
            # Summary Section
            self._add_section_header('Summary', '')
            self._add_box_content(analysis.get('summary', 'N/A'), 'summary')
            
            # Tone & Intent with visual indicators
            self._add_section_header('Tone & Intent Analysis', '')
            self._add_tone_intent_section(analysis)
            
            # Sentiment with visual bar
            self._add_section_header('Sentiment Analysis', '')
            self._add_sentiment_section(analysis)
            
            # Priority with colored badge
            self._add_section_header('Priority Level', '')
            self._add_priority_section(analysis)
            
            # Key Points
            self._add_section_header('Key Points', '')
            key_points = analysis.get('key_points', [])
            if key_points:
                for point in key_points[:6]:
                    self._add_bullet(point, (34, 197, 94))
            else:
                self._add_content('No key points identified')
            self.pdf.ln(3)
            
            # Action Items
            self._add_section_header('Action Items', '')
            action_items = analysis.get('action_items', [])
            if action_items:
                for item in action_items:
                    self._add_action_item(item)
            else:
                self._add_content('No specific action items identified')
            self.pdf.ln(3)
            
            # Suggested Reply
            self._add_section_header('Suggested Professional Reply', '')
            self._add_box_content(analysis.get('suggested_reply', 'N/A'), 'reply')
            
            # Generate and add charts
            self._add_section_header('Visual Analysis Charts', '')
            self._add_charts(analysis)
            
            # Generate PDF bytes with proper encoding
            try:
                pdf_output = self.pdf.output(dest='S')
                if isinstance(pdf_output, str):
                    return pdf_output.encode('latin-1')
                elif isinstance(pdf_output, bytearray):
                    return bytes(pdf_output)
                return pdf_output
            except Exception as output_error:
                print(f"PDF output error: {output_error}")
                # Fallback method
                try:
                    return bytes(self.pdf.output())
                except Exception as fallback_error:
                    print(f"Fallback PDF output error: {fallback_error}")
                    # Final fallback - create minimal PDF
                    return self._create_minimal_pdf()
        except Exception as e:
            error_msg = str(e).replace('\U0001f4e7', '').replace('\ud83d\udce7', '')
            print(f"PDF Generation Error: {error_msg}")
            raise Exception(f"Failed to generate PDF: {error_msg}")
    
    def _add_stats_box(self, analysis):
        """Add a colorful stats box at the top"""
        y_start = self.pdf.get_y()
        
        # Background box
        bg_color = self.card_bg if hasattr(self, 'card_bg') else (248, 250, 252)
        self.pdf.set_fill_color(*bg_color)
        self.pdf.rect(10, y_start, 190, 25, 'F')
        
        # Stats - adjust text color based on theme
        text_gray = (200, 200, 210) if hasattr(self, '_theme') and self._theme == 'dark' else (107, 114, 128)
        
        # Stats
        stats = [
            ('Tone', analysis.get('tone', 'N/A'), (99, 102, 241)),
            ('Intent', analysis.get('intent', 'N/A'), (168, 85, 247)),
            ('Sentiment', analysis.get('sentiment', 'N/A'), (236, 72, 153)),
            ('Priority', analysis.get('priority', 'N/A'), (249, 115, 22))
        ]
        
        x_pos = 15
        for label, value, color in stats:
            self.pdf.set_xy(x_pos, y_start + 5)
            self.pdf.set_font('Arial', 'B', 8)
            self.pdf.set_text_color(*text_gray)
            self.pdf.cell(40, 4, label, ln=True)
            
            self.pdf.set_xy(x_pos, y_start + 10)
            self.pdf.set_font('Arial', 'B', 11)
            self.pdf.set_text_color(*color)
            self.pdf.cell(40, 6, value[:15], ln=True)
            
            x_pos += 47
        
        self.pdf.set_text_color(*self.text_color)
        self.pdf.set_y(y_start + 30)
    
    def _add_tone_intent_section(self, analysis):
        """Add tone and intent with confidence bar"""
        # Tone
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(99, 102, 241)
        self.pdf.cell(30, 6, 'Tone:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.text_color)
        tone_text = self._clean_text(str(analysis.get('tone', 'N/A')))
        self.pdf.cell(0, 6, tone_text, ln=True)
        
        self.pdf.set_font('Arial', 'I', 9)
        text_gray = (200, 200, 210) if self._theme == 'dark' else (107, 114, 128)
        self.pdf.set_text_color(*text_gray)
        reasoning_text = self._clean_text(str(analysis.get('tone_reasoning', 'N/A')))
        self.pdf.multi_cell(0, 5, reasoning_text)
        self.pdf.ln(2)
        
        # Intent
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(168, 85, 247)
        self.pdf.cell(30, 6, 'Intent:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.text_color)
        intent_text = self._clean_text(str(analysis.get('intent', 'N/A')))
        self.pdf.cell(0, 6, intent_text, ln=True)
        
        # Confidence bar
        confidence_str = str(analysis.get('confidence', '0%'))
        confidence = int(confidence_str.replace('%', ''))
        self._add_progress_bar(confidence, 'Confidence', (99, 102, 241))
        self.pdf.ln(3)
    
    def _add_sentiment_section(self, analysis):
        """Add sentiment with polarity visualization"""
        sentiment = self._clean_text(str(analysis.get('sentiment', 'N/A')))
        polarity = float(analysis.get('polarity', 0))
        emotion = self._clean_text(str(analysis.get('emotion', 'N/A')))
        
        # Sentiment
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(236, 72, 153)
        self.pdf.cell(40, 6, 'Sentiment:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.cell(0, 6, f'{sentiment} (Polarity: {polarity})', ln=True)
        
        # Polarity bar (-1 to +1)
        self._add_polarity_bar(polarity)
        
        # Emotion
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(236, 72, 153)
        self.pdf.cell(40, 6, 'Emotion:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.cell(0, 6, emotion, ln=True)
        self.pdf.ln(3)
    
    def _add_priority_section(self, analysis):
        """Add priority with colored badge"""
        priority = self._clean_text(str(analysis.get('priority', 'N/A')))
        priority_reason = self._clean_text(str(analysis.get('priority_reason', 'N/A')))
        
        # Priority badge
        y_pos = self.pdf.get_y()
        
        # Color based on priority
        colors = {
            'Critical': (220, 38, 38),
            'High': (234, 88, 12),
            'Medium': (234, 179, 8),
            'Low': (34, 197, 94)
        }
        color = colors.get(priority, (107, 114, 128))
        
        # Badge background
        self.pdf.set_fill_color(*color)
        self.pdf.rect(10, y_pos, 40, 8, 'F')
        
        # Badge text
        self.pdf.set_xy(10, y_pos)
        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.cell(40, 8, priority, align='C')
        
        # Reason
        self.pdf.set_xy(10, y_pos + 10)
        self.pdf.set_font('Arial', '', 9)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.multi_cell(0, 5, f'Reason: {priority_reason}')
        self.pdf.ln(3)
    
    def _add_progress_bar(self, percentage, label, color):
        """Add a visual progress bar"""
        y_pos = self.pdf.get_y()
        
        # Label
        self.pdf.set_font('Arial', '', 9)
        text_gray = (200, 200, 210) if self._theme == 'dark' else (107, 114, 128)
        self.pdf.set_text_color(*text_gray)
        self.pdf.cell(0, 5, f'{label}: {percentage}%', ln=True)
        
        # Bar background
        bar_bg = (50, 50, 65) if self._theme == 'dark' else (229, 231, 235)
        self.pdf.set_fill_color(*bar_bg)
        self.pdf.rect(10, self.pdf.get_y(), 190, 6, 'F')
        
        # Bar fill
        bar_width = (190 * percentage) / 100
        self.pdf.set_fill_color(*color)
        self.pdf.rect(10, self.pdf.get_y(), bar_width, 6, 'F')
        
        self.pdf.ln(8)
    
    def _add_polarity_bar(self, polarity):
        """Add polarity visualization bar from -1 to +1"""
        y_pos = self.pdf.get_y()
        
        # Label
        self.pdf.set_font('Arial', '', 9)
        text_gray = (200, 200, 210) if self._theme == 'dark' else (107, 114, 128)
        self.pdf.set_text_color(*text_gray)
        self.pdf.cell(0, 5, 'Polarity Scale (-1 = Negative, 0 = Neutral, +1 = Positive)', ln=True)
        
        # Gradient bar (red to yellow to green)
        bar_y = self.pdf.get_y()
        segments = 19
        segment_width = 190 / segments
        
        for i in range(segments):
            # Calculate color gradient
            if i < segments / 2:
                # Red to Yellow
                r = 239
                g = int(68 + (187 * (i / (segments / 2))))
                b = 68
            else:
                # Yellow to Green
                r = int(251 - (217 * ((i - segments / 2) / (segments / 2))))
                g = int(191 + (66 * ((i - segments / 2) / (segments / 2))))
                b = int(36 + (58 * ((i - segments / 2) / (segments / 2))))
            
            self.pdf.set_fill_color(r, g, b)
            self.pdf.rect(10 + (i * segment_width), bar_y, segment_width, 6, 'F')
        
        # Indicator - white for dark theme, black for light
        indicator_color = (255, 255, 255) if self._theme == 'dark' else (0, 0, 0)
        indicator_pos = 10 + ((polarity + 1) / 2) * 190
        self.pdf.set_fill_color(*indicator_color)
        self.pdf.rect(indicator_pos - 1, bar_y - 2, 2, 10, 'F')
        
        self.pdf.ln(10)
    
    def _add_action_item(self, item):
        """Add styled action item"""
        y_pos = self.pdf.get_y()
        
        # Clean the action text
        action_text = self._clean_text(str(item.get('action', 'N/A')))
        responsibility_text = self._clean_text(str(item.get('responsibility', 'N/A')))
        
        # Box background - theme aware
        if self._theme == 'dark':
            box_bg = (30, 50, 40)
        else:
            box_bg = (240, 253, 244)
        self.pdf.set_fill_color(*box_bg)
        self.pdf.rect(10, y_pos, 190, 12, 'F')
        
        # Checkmark
        self.pdf.set_xy(12, y_pos + 2)
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(34, 197, 94)
        self.pdf.cell(5, 8, chr(252))
        
        # Action text
        self.pdf.set_xy(20, y_pos + 2)
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.multi_cell(170, 4, action_text)
        
        # Responsibility
        self.pdf.set_xy(20, y_pos + 7)
        self.pdf.set_font('Arial', 'I', 8)
        text_gray = (200, 200, 210) if self._theme == 'dark' else (107, 114, 128)
        self.pdf.set_text_color(*text_gray)
        self.pdf.cell(0, 4, f"Responsibility: {responsibility_text}")
        
        self.pdf.set_y(y_pos + 14)
    
    def _add_section_header(self, title, emoji=''):
        """Add colorful section header"""
        self.pdf.ln(2)
        y_pos = self.pdf.get_y()
        
        # Accent line
        self.pdf.set_fill_color(99, 102, 241)
        self.pdf.rect(10, y_pos, 3, 8, 'F')
        
        # Title
        self.pdf.set_xy(15, y_pos)
        self.pdf.set_font('Arial', 'B', 13)
        self.pdf.set_text_color(99, 102, 241)
        self.pdf.cell(0, 8, title, ln=True)
        
        self.pdf.set_text_color(*self.text_color)
        self.pdf.ln(2)
    
    def _add_box_content(self, text, bg_color_key='email'):
        """Add content in a colored box"""
        y_start = self.pdf.get_y()
        
        # Clean text
        text = self._clean_text(str(text))
        
        # Get color based on theme
        if hasattr(self, 'box_colors'):
            bg_color = self.box_colors.get(bg_color_key, self.card_bg)
        else:
            bg_color = bg_color_key if isinstance(bg_color_key, tuple) else self.card_bg
        
        # Calculate height needed
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.text_color)
        lines = len(self.pdf.multi_cell(190, 5, text, split_only=True))
        box_height = (lines * 5) + 6
        
        # Draw box
        self.pdf.set_fill_color(*bg_color)
        self.pdf.rect(10, y_start, 190, box_height, 'F')
        
        # Add text
        self.pdf.set_xy(13, y_start + 3)
        self.pdf.multi_cell(184, 5, text)
        self.pdf.ln(3)
    
    def _add_content(self, text):
        """Add regular content"""
        text = self._clean_text(str(text))
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.multi_cell(0, 5, text)
        self.pdf.ln(2)
    
    def _add_bullet(self, text, color=(99, 102, 241)):
        """Add colored bullet point"""
        y_pos = self.pdf.get_y()
        
        # Clean text
        text = self._clean_text(str(text))
        
        # Bullet
        self.pdf.set_xy(12, y_pos)
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(*color)
        self.pdf.cell(5, 5, chr(149))
        
        # Text
        self.pdf.set_xy(18, y_pos)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_text_color(*self.text_color)
        self.pdf.multi_cell(182, 5, text)
    
    def _clean_text(self, text):
        """Clean text to remove problematic characters for PDF generation"""
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '\u2019': "'",  # Right single quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Horizontal ellipsis
            '\u00a0': ' ',  # Non-breaking space
            '\u2022': '*',  # Bullet
            '\u2010': '-',  # Hyphen
            '\u2011': '-',  # Non-breaking hyphen
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Remove or replace other problematic Unicode characters
        import re
        # Remove emojis and other special Unicode characters
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        return text.strip()
    
    def _clean_analysis_data(self, analysis):
        """Clean analysis data to remove problematic characters"""
        if not isinstance(analysis, dict):
            return analysis
        
        cleaned = {}
        for key, value in analysis.items():
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_text(str(item)) if isinstance(item, str) else item for item in value]
            elif isinstance(value, dict):
                cleaned[key] = self._clean_analysis_data(value)
            else:
                cleaned[key] = value
        return cleaned
    
    def _add_footer_to_current_page(self):
        """Add footer to the current page at the bottom"""
        # Move to bottom of page (accounting for margin)
        self.pdf.set_y(265)  # Fixed position near bottom
        
        # Footer bar
        y_pos = self.pdf.get_y()
        self.pdf.set_fill_color(99, 102, 241)
        self.pdf.rect(0, y_pos, 210, 20, 'F')
        
        # Generated by text
        self.pdf.set_xy(10, y_pos + 3)
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.cell(0, 5, 'Generated by CommAI - AI-Powered Email Analyzer', align='C', ln=True)
        
        # User email, date, and time
        from datetime import datetime
        current_time = datetime.now()
        date_str = current_time.strftime('%B %d, %Y')
        time_str = current_time.strftime('%I:%M %p')
        
        # Get user email from the instance if available
        info_parts = []
        if hasattr(self, '_user_email') and self._user_email:
            info_parts.append(f'User: {self._user_email}')
        info_parts.append(f'Date: {date_str}')
        info_parts.append(f'Time: {time_str}')
        
        info_text = '  |  '.join(info_parts)
        
        self.pdf.set_xy(10, y_pos + 10)
        self.pdf.set_font('Arial', 'I', 8)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.cell(0, 5, info_text, align='C')
    
    def _add_charts(self, analysis):
        """Generate and add charts to PDF"""
        try:
            polarity = float(analysis.get('polarity', 0))
            polarity_score = ((polarity + 1) / 2) * 100
            confidence_score = int(analysis.get('confidence', '50%').replace('%', ''))
            subjectivity = float(analysis.get('subjectivity', 0.5))
            subjectivity_score = subjectivity * 100

            tone_scores = {'Formal': 90, 'Friendly': 75, 'Neutral': 50, 'Negative': 30, 'Apologetic': 60}
            tone_score = tone_scores.get(analysis.get('tone', 'Neutral'), 50)

            sentiment_scores = {'Positive': 85, 'Neutral': 50, 'Negative': 20}
            sentiment_score = sentiment_scores.get(analysis.get('sentiment', 'Neutral'), 50)

            radar_file = self._create_radar_chart(sentiment_score, confidence_score, tone_score, polarity_score, subjectivity_score)
            bar_file = self._create_bar_chart(sentiment_score, confidence_score, tone_score, polarity_score)
            pie_file = self._create_pie_chart(analysis.get('priority', 'Medium'))

            import os
            
            # Always start charts on a new page for proper alignment
            self.pdf.add_page()
            self.pdf.set_y(45)  # Start below header
            
            # Radar and Bar charts side by side
            if radar_file and os.path.exists(radar_file) and bar_file and os.path.exists(bar_file):
                # Titles
                self.pdf.set_font('Arial', 'B', 11)
                self.pdf.set_text_color(99, 102, 241)
                self.pdf.set_x(10)
                self.pdf.cell(95, 6, 'Sentiment & Tone Overview', ln=0, align='C')
                
                self.pdf.set_x(105)
                self.pdf.cell(95, 6, 'Analysis Scores', ln=True, align='C')
                self.pdf.ln(2)
                
                # Add both charts side by side
                chart_y = self.pdf.get_y()
                self.pdf.image(radar_file, x=10, y=chart_y, w=90)
                self.pdf.image(bar_file, x=105, y=chart_y, w=90)
                
                # Move below the charts
                self.pdf.set_y(chart_y + 75)
                self.pdf.ln(5)
                
                os.remove(radar_file)
                os.remove(bar_file)
            
            # Pie chart centered below
            if pie_file and os.path.exists(pie_file):
                current_y = self.pdf.get_y()
                
                # Check if we need a new page for pie chart
                if current_y > 180:  # Not enough space
                    self.pdf.add_page()
                    current_y = 45
                    self.pdf.set_y(current_y)
                
                # Pie chart title
                self.pdf.set_font('Arial', 'B', 11)
                self.pdf.set_text_color(99, 102, 241)
                self.pdf.cell(0, 6, 'Priority Distribution', ln=True, align='C')
                self.pdf.ln(2)
                
                # Centered pie chart
                chart_y = self.pdf.get_y()
                self.pdf.image(pie_file, x=50, y=chart_y, w=110)
                
                # Move to end of pie chart
                self.pdf.set_y(chart_y + 90)
                
                os.remove(pie_file)
            
            # Add footer on the last page
            self._add_footer_to_current_page()

        except Exception as e:
            print(f"Chart generation error: {e}")
            self.pdf.set_font('Arial', 'I', 10)
            self.pdf.set_text_color(107, 114, 128)
            self.pdf.cell(0, 6, 'Charts could not be generated', ln=True)
            self._add_footer_to_current_page()
    
    def _create_radar_chart(self, sentiment, confidence, tone, polarity, clarity):
        """Create radar chart"""
        try:
            # Set dark background if dark theme
            if self._theme == 'dark':
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(6, 5), subplot_kw=dict(projection='polar'), facecolor='#1e1e2d')
                ax.set_facecolor('#1e1e2d')
                text_color = '#f0f0f5'
                grid_color = '#4a4a5f'
            else:
                fig, ax = plt.subplots(figsize=(6, 5), subplot_kw=dict(projection='polar'), facecolor='white')
                ax.set_facecolor('white')
                text_color = '#1f2937'
                grid_color = '#e5e7eb'
            
            categories = ['Sentiment', 'Confidence', 'Tone', 'Polarity', 'Clarity']
            values = [sentiment, confidence, tone, polarity, clarity]
            
            N = len(categories)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            values += values[:1]
            angles += angles[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2.5, color='#6366f1')
            ax.fill(angles, values, alpha=0.3, color='#6366f1')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, size=10, fontweight='bold', color=text_color)
            ax.set_ylim(0, 100)
            ax.yaxis.set_tick_params(labelsize=9, colors=text_color)
            ax.set_title('Sentiment & Tone', size=12, pad=15, fontweight='bold', color=text_color)
            ax.grid(True, linewidth=1, color=grid_color, alpha=0.3)
            ax.spines['polar'].set_color(grid_color)
            
            temp_file = 'temp_radar.png'
            plt.tight_layout()
            bg_color = '#1e1e2d' if self._theme == 'dark' else 'white'
            plt.savefig(temp_file, dpi=100, bbox_inches='tight', facecolor=bg_color)
            plt.close()
            plt.style.use('default')  # Reset style
            return temp_file
        except Exception as e:
            print(f"Radar chart error: {e}")
            plt.style.use('default')  # Reset style on error
            return None
    
    def _create_bar_chart(self, sentiment, confidence, tone, polarity):
        """Create bar chart"""
        try:
            # Set dark background if dark theme
            if self._theme == 'dark':
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(6, 4.5), facecolor='#1e1e2d')
                ax.set_facecolor('#1e1e2d')
                text_color = '#f0f0f5'
                grid_color = '#4a4a5f'
            else:
                fig, ax = plt.subplots(figsize=(6, 4.5), facecolor='white')
                ax.set_facecolor('white')
                text_color = '#1f2937'
                grid_color = '#e5e7eb'
            
            categories = ['Sentiment', 'Confidence', 'Tone', 'Polarity']
            values = [sentiment, confidence, tone, polarity]
            colors = ['#22c55e', '#6366f1', '#a855f7', '#ec4899']
            
            bars = ax.bar(categories, values, color=colors, alpha=0.85, edgecolor=text_color, linewidth=1.2, width=0.5)
            
            ax.set_ylim(0, 110)
            ax.set_ylabel('Score (%)', fontsize=10, fontweight='bold', color=text_color)
            ax.set_title('Analysis Scores', fontsize=12, pad=10, fontweight='bold', color=text_color)
            ax.tick_params(axis='both', labelsize=10, colors=text_color)
            ax.grid(axis='y', alpha=0.3, linewidth=1, color=grid_color)
            ax.spines['bottom'].set_color(grid_color)
            ax.spines['top'].set_color(grid_color)
            ax.spines['left'].set_color(grid_color)
            ax.spines['right'].set_color(grid_color)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{int(height)}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color=text_color)
            
            temp_file = 'temp_bar.png'
            plt.tight_layout()
            bg_color = '#1e1e2d' if self._theme == 'dark' else 'white'
            plt.savefig(temp_file, dpi=100, bbox_inches='tight', facecolor=bg_color)
            plt.close()
            plt.style.use('default')  # Reset style
            return temp_file
        except Exception as e:
            print(f"Bar chart error: {e}")
            plt.style.use('default')  # Reset style on error
            return None
    
    def _create_pie_chart(self, priority):
        """Create pie chart"""
        try:
            # Set dark background if dark theme
            if self._theme == 'dark':
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(6, 5), facecolor='#1e1e2d')
                ax.set_facecolor('#1e1e2d')
                text_color = '#f0f0f5'
                center_color = '#1e1e2d'
            else:
                fig, ax = plt.subplots(figsize=(6, 5), facecolor='white')
                ax.set_facecolor('white')
                text_color = '#1f2937'
                center_color = 'white'
            
            priority_weights = {
                'Critical': [90, 5, 3, 2],
                'High': [20, 60, 15, 5],
                'Medium': [10, 20, 50, 20],
                'Low': [5, 10, 20, 65]
            }
            
            weights = priority_weights.get(priority, [25, 25, 25, 25])
            labels = ['Critical', 'High', 'Medium', 'Low']
            colors = ['#dc2626', '#ea580c', '#eab308', '#22c55e']
            
            wedges, texts, autotexts = ax.pie(
                weights, labels=labels, colors=colors, autopct='%1.0f%%',
                startangle=90, textprops={'fontsize': 11, 'color': text_color},
                wedgeprops={'linewidth': 2, 'edgecolor': center_color},
                pctdistance=0.75
            )
            for at in autotexts:
                at.set_fontsize(10)
                at.set_fontweight('bold')
                at.set_color('white')  # Percentage text always white for visibility
            
            centre_circle = Circle((0, 0), 0.60, fc=center_color)
            ax.add_artist(centre_circle)
            ax.text(0, 0, priority, ha='center', va='center', fontsize=14, fontweight='bold', color=text_color)
            
            ax.set_title('Priority Distribution', fontsize=12, pad=12, fontweight='bold', color=text_color)
            
            temp_file = 'temp_pie.png'
            plt.tight_layout()
            bg_color = '#1e1e2d' if self._theme == 'dark' else 'white'
            plt.savefig(temp_file, dpi=100, bbox_inches='tight', facecolor=bg_color)
            plt.close()
            plt.style.use('default')  # Reset style
            return temp_file
        except Exception as e:
            print(f"Pie chart error: {e}")
            plt.style.use('default')  # Reset style on error
            return None
    
    def _create_minimal_pdf(self):
        """Create a minimal PDF as final fallback"""
        try:
            minimal_pdf = FPDF()
            minimal_pdf.add_page()
            minimal_pdf.set_font('Arial', 'B', 16)
            minimal_pdf.cell(0, 10, 'Email Analysis Report', ln=True, align='C')
            minimal_pdf.ln(10)
            minimal_pdf.set_font('Arial', '', 12)
            minimal_pdf.cell(0, 10, 'Report generation encountered an error.', ln=True)
            minimal_pdf.cell(0, 10, 'Please try again or contact support.', ln=True)
            
            output = minimal_pdf.output(dest='S')
            if isinstance(output, str):
                return output.encode('latin-1')
            elif isinstance(output, bytearray):
                return bytes(output)
            return output
        except Exception as e:
            print(f"Minimal PDF creation failed: {e}")
            # Return empty bytes as absolute last resort
            return b''
