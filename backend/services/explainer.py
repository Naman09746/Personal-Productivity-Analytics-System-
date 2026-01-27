"""
Explainer - Generate insights about score changes
"""
from datetime import date, timedelta
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from services.score_engine import ScoreEngine


class Explainer:
    """Generates human-readable explanations for score changes"""
    
    @staticmethod
    async def explain_weekly_change(
        db: AsyncSession,
        user_id,
        current_week: date
    ) -> List[Dict]:
        """Explain why this week's score differs from last week"""
        insights = []
        
        # Get current and previous week scores
        current_score = await ScoreEngine.calculate_weekly_score(db, user_id, current_week)
        previous_week = current_week - timedelta(days=7)
        previous_score = await ScoreEngine.calculate_weekly_score(db, user_id, previous_week)
        
        if not previous_score["habit_breakdown"]:
            insights.append({
                "icon": "🆕",
                "message": "First week of tracking! Keep building your habits.",
                "impact": 0
            })
            return insights
        
        # Compare overall scores
        rate_diff = current_score["completion_rate"] - previous_score["completion_rate"]
        if abs(rate_diff) >= 5:
            if rate_diff > 0:
                insights.append({
                    "icon": "📈",
                    "message": f"Completion rate improved by {rate_diff:.1f}%",
                    "impact": rate_diff
                })
            else:
                insights.append({
                    "icon": "📉",
                    "message": f"Completion rate dropped by {abs(rate_diff):.1f}%",
                    "impact": rate_diff
                })
        
        # Build lookup for previous week habits
        prev_habits = {h["habit_id"]: h for h in previous_score["habit_breakdown"]}
        
        # Compare individual habits
        for habit in current_score["habit_breakdown"]:
            habit_id = habit["habit_id"]
            prev_habit = prev_habits.get(habit_id)
            
            if not prev_habit:
                insights.append({
                    "icon": "🆕",
                    "message": f"New habit '{habit['habit_name']}' added",
                    "impact": habit["weighted_contribution"]
                })
                continue
            
            habit_diff = habit["completion_rate"] - prev_habit["completion_rate"]
            
            # Significant change (>20%)
            if habit_diff >= 20:
                insights.append({
                    "icon": "🚀",
                    "message": f"'{habit['habit_name']}' improved from {prev_habit['completion_rate']:.0f}% to {habit['completion_rate']:.0f}%",
                    "impact": habit_diff * habit["weight"] / 100
                })
            elif habit_diff <= -20:
                insights.append({
                    "icon": "⚠️",
                    "message": f"'{habit['habit_name']}' dropped from {prev_habit['completion_rate']:.0f}% to {habit['completion_rate']:.0f}%",
                    "impact": habit_diff * habit["weight"] / 100
                })
            
            # Check threshold violations
            if habit["is_below_threshold"] and not prev_habit.get("is_below_threshold", False):
                insights.append({
                    "icon": "🔔",
                    "message": f"'{habit['habit_name']}' is now below your {habit.get('goal_threshold', 80)}% goal",
                    "impact": -5
                })
        
        # Consistency insight
        consistency_diff = current_score["consistency_score"] - previous_score["consistency_score"]
        if consistency_diff >= 10:
            insights.append({
                "icon": "🎯",
                "message": "Your daily consistency improved significantly",
                "impact": consistency_diff / 10
            })
        elif consistency_diff <= -10:
            insights.append({
                "icon": "📊",
                "message": "Your habit completion was less consistent this week",
                "impact": consistency_diff / 10
            })
        
        # Sort by impact (most impactful first)
        insights.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        return insights[:5]  # Top 5 insights
    
    @staticmethod
    def generate_grade(avg_score: float) -> str:
        """Convert average score to letter grade"""
        if avg_score >= 95:
            return "A+"
        elif avg_score >= 90:
            return "A"
        elif avg_score >= 85:
            return "A-"
        elif avg_score >= 80:
            return "B+"
        elif avg_score >= 75:
            return "B"
        elif avg_score >= 70:
            return "B-"
        elif avg_score >= 65:
            return "C+"
        elif avg_score >= 60:
            return "C"
        elif avg_score >= 55:
            return "C-"
        elif avg_score >= 50:
            return "D"
        else:
            return "F"
