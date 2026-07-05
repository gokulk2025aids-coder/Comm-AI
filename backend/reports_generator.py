import json
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class ReportsGenerator:
    def __init__(self, database):
        self.db = database
    
    def get_user_analyses_by_period(self, user_id, period='week'):
        """Get user analyses for a specific period (week/month)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Calculate date range
            now = datetime.now()
            if period == 'week':
                start_date = (now - timedelta(days=7)).isoformat()
            elif period == 'month':
                start_date = (now - timedelta(days=30)).isoformat()
            else:
                start_date = (now - timedelta(days=7)).isoformat()
            
            cursor.execute("""
                SELECT id, email_text, analysis_result, created_at 
                FROM analyses 
                WHERE user_id = ? AND created_at >= ?
                ORDER BY created_at ASC
            """, (user_id, start_date))
            
            results = cursor.fetchall()
            return [{
                "id": r[0],
                "email_text": r[1],
                "analysis": json.loads(r[2]),
                "created_at": r[3]
            } for r in results]
        except Exception as e:
            logger.error(f"Error fetching analyses by period: {e}")
            return []
        finally:
            conn.close()
    
    def generate_report(self, user_id, period='week'):
        """Generate comprehensive report for user"""
        analyses = self.get_user_analyses_by_period(user_id, period)
        
        if not analyses:
            return {
                "success": False,
                "message": f"No analyses found for the past {period}"
            }
        
        # Calculate statistics
        total_emails = len(analyses)
        
        # Extract scores
        professionalism_scores = []
        overall_scores = []
        readability_scores = []
        clarity_scores = []
        engagement_scores = []
        
        tones = []
        intents = []
        sentiments = []
        priorities = []
        grammar_issues_count = []
        
        for analysis in analyses:
            a = analysis['analysis']
            
            # Scores
            if 'professionalism_score' in a:
                professionalism_scores.append(float(a['professionalism_score']))
            
            if 'email_scores' in a:
                scores = a['email_scores']
                overall_scores.append(scores.get('overall_score', 0))
                readability_scores.append(scores.get('readability_score', 0))
                clarity_scores.append(scores.get('clarity_score', 0))
                engagement_scores.append(scores.get('engagement_score', 0))
            
            # Categories
            if 'tone' in a:
                tones.append(a['tone'])
            if 'intent' in a:
                intents.append(a['intent'])
            if 'sentiment' in a:
                sentiments.append(a['sentiment'])
            if 'priority' in a:
                priorities.append(a['priority'])
            if 'grammar_issues' in a:
                grammar_issues_count.append(len(a['grammar_issues']))
        
        # Calculate averages
        avg_professionalism = sum(professionalism_scores) / len(professionalism_scores) if professionalism_scores else 0
        avg_overall = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        avg_readability = sum(readability_scores) / len(readability_scores) if readability_scores else 0
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        avg_grammar_issues = sum(grammar_issues_count) / len(grammar_issues_count) if grammar_issues_count else 0
        
        # Calculate trends (compare first half vs second half)
        mid_point = len(professionalism_scores) // 2
        if mid_point > 0:
            first_half_prof = sum(professionalism_scores[:mid_point]) / mid_point
            second_half_prof = sum(professionalism_scores[mid_point:]) / (len(professionalism_scores) - mid_point)
            prof_trend = second_half_prof - first_half_prof
            
            first_half_overall = sum(overall_scores[:mid_point]) / mid_point if mid_point <= len(overall_scores) else 0
            second_half_overall = sum(overall_scores[mid_point:]) / (len(overall_scores) - mid_point) if mid_point < len(overall_scores) else 0
            overall_trend = second_half_overall - first_half_overall
        else:
            prof_trend = 0
            overall_trend = 0
        
        # Most common categories
        most_common_tone = max(set(tones), key=tones.count) if tones else "N/A"
        most_common_intent = max(set(intents), key=intents.count) if intents else "N/A"
        most_common_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "N/A"
        most_common_priority = max(set(priorities), key=priorities.count) if priorities else "N/A"
        
        # Identify improvements and areas needing work
        improvements = []
        needs_work = []
        
        # Check professionalism trend
        if prof_trend > 0.5:
            improvements.append({
                "area": "Professionalism",
                "improvement": f"+{prof_trend:.1f} points",
                "description": "Your professional writing quality has improved"
            })
        elif prof_trend < -0.5:
            needs_work.append({
                "area": "Professionalism",
                "decline": f"{prof_trend:.1f} points",
                "description": "Professional quality has declined, focus on formal language"
            })
        
        # Check overall quality trend
        if overall_trend > 5:
            improvements.append({
                "area": "Overall Quality",
                "improvement": f"+{overall_trend:.1f} points",
                "description": "Your overall email quality has improved significantly"
            })
        elif overall_trend < -5:
            needs_work.append({
                "area": "Overall Quality",
                "decline": f"{overall_trend:.1f} points",
                "description": "Overall quality needs attention"
            })
        
        # Check grammar
        if avg_grammar_issues > 3:
            needs_work.append({
                "area": "Grammar & Spelling",
                "issue": f"Average {avg_grammar_issues:.1f} issues per email",
                "description": "Focus on proofreading before sending"
            })
        elif avg_grammar_issues < 1:
            improvements.append({
                "area": "Grammar & Spelling",
                "achievement": f"Only {avg_grammar_issues:.1f} issues per email",
                "description": "Excellent attention to detail"
            })
        
        # Check clarity
        if avg_clarity < 60:
            needs_work.append({
                "area": "Clarity",
                "score": f"{avg_clarity:.1f}/100",
                "description": "Messages could be clearer and more direct"
            })
        elif avg_clarity > 80:
            improvements.append({
                "area": "Clarity",
                "score": f"{avg_clarity:.1f}/100",
                "description": "Your messages are clear and easy to understand"
            })
        
        # Check engagement
        if avg_engagement < 50:
            needs_work.append({
                "area": "Engagement",
                "score": f"{avg_engagement:.1f}/100",
                "description": "Try to make emails more engaging with questions or calls-to-action"
            })
        elif avg_engagement > 70:
            improvements.append({
                "area": "Engagement",
                "score": f"{avg_engagement:.1f}/100",
                "description": "Your emails are engaging and capture attention"
            })
        
        # Writing trends
        trends = {
            "professionalism_trend": {
                "direction": "improving" if prof_trend > 0.5 else "declining" if prof_trend < -0.5 else "stable",
                "change": round(prof_trend, 2)
            },
            "overall_quality_trend": {
                "direction": "improving" if overall_trend > 5 else "declining" if overall_trend < -5 else "stable",
                "change": round(overall_trend, 2)
            },
            "most_used_tone": most_common_tone,
            "most_common_intent": most_common_intent,
            "dominant_sentiment": most_common_sentiment,
            "typical_priority": most_common_priority
        }
        
        # Generate insights
        insights = []
        
        if avg_professionalism >= 8:
            insights.append("🌟 Excellent professional writing - keep it up!")
        elif avg_professionalism < 5:
            insights.append("⚠️ Professional quality needs improvement - review formal writing guidelines")
        
        if most_common_sentiment == "Negative":
            insights.append("💡 Consider using more positive language in your emails")
        elif most_common_sentiment == "Positive":
            insights.append("😊 Great job maintaining positive communication")
        
        if avg_grammar_issues > 5:
            insights.append("📝 High grammar error rate - consider using spell-check tools")
        
        if most_common_tone == "Negative":
            insights.append("🎭 Your tone tends to be negative - try diplomatic phrasing")
        
        # Build report
        report = {
            "success": True,
            "period": period,
            "period_label": "Last 7 Days" if period == 'week' else "Last 30 Days",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_emails_analyzed": total_emails,
                "average_professionalism": round(avg_professionalism, 1),
                "average_overall_quality": round(avg_overall, 1),
                "average_readability": round(avg_readability, 1),
                "average_clarity": round(avg_clarity, 1),
                "average_engagement": round(avg_engagement, 1),
                "average_grammar_issues": round(avg_grammar_issues, 1)
            },
            "most_improved_areas": improvements if improvements else [{"area": "No significant improvements yet", "description": "Keep analyzing emails to track progress"}],
            "areas_needing_work": needs_work if needs_work else [{"area": "Great job!", "description": "No major areas of concern identified"}],
            "writing_trends": trends,
            "insights": insights if insights else ["Continue analyzing emails to generate insights"],
            "score_breakdown": {
                "professionalism_scores": professionalism_scores,
                "overall_scores": overall_scores,
                "readability_scores": readability_scores,
                "clarity_scores": clarity_scores,
                "engagement_scores": engagement_scores
            }
        }
        
        return report
