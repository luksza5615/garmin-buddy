import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.services.db_service import get_activities_last_x_days
from app.services.llm_google_service import generate_response


class WeeklyAnalysisService:
    """
    Service for analyzing training data over configurable time periods.
    Supports flexible day ranges (7, 10, 21 days, etc.) for comprehensive analysis.
    """
    
    def __init__(self):
        self.llm_service = None  # Will be injected or imported as needed
    
    def get_activities_data(self, days: int = 7) -> pd.DataFrame:
        """
        Fetch activities from the last X days.
        
        Args:
            days (int): Number of days to look back (default: 7)
            
        Returns:
            pd.DataFrame: Activities data for the specified period
        """
        return get_activities_last_x_days(days)
    
    def calculate_weekly_metrics(self, activities_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate aggregated metrics from activities data.
        
        Args:
            activities_df (pd.DataFrame): Activities data
            
        Returns:
            Dict[str, Any]: Calculated metrics
        """
        if activities_df.empty:
            return {
                'total_activities': 0,
                'total_distance_km': 0,
                'total_duration_hours': 0,
                'avg_heart_rate': 0,
                'total_calories': 0,
                'total_ascent_m': 0,
                'sports_breakdown': {},
                'avg_efficiency_index': 0,
                'avg_training_effect': 0
            }
        
        # Convert duration to hours for total calculation
        activities_df['duration_hours'] = pd.to_timedelta(activities_df['elapsed_duration']).dt.total_seconds() / 3600
        
        metrics = {
            'total_activities': len(activities_df),
            'total_distance_km': activities_df['distance_in_km'].sum(),
            'total_duration_hours': round(activities_df['duration_hours'].sum(), 2),
            'avg_heart_rate': round(activities_df['avg_heart_rate'].mean(), 1),
            'total_calories': activities_df['calories_burnt'].sum(),
            'total_ascent_m': activities_df['total_ascent_in_meters'].sum(),
            'sports_breakdown': activities_df['sport'].value_counts().to_dict(),
            'avg_efficiency_index': round(activities_df['running_efficiency_index'].mean(), 2) if 'running_efficiency_index' in activities_df.columns else 0,
            'avg_training_effect': round(activities_df['aerobic_training_effect_0_to_5'].mean(), 2) if 'aerobic_training_effect_0_to_5' in activities_df.columns else 0
        }
        
        return metrics
    
    def format_activities_for_prompt(self, activities_df: pd.DataFrame) -> str:
        """
        Format activities data into a readable string for LLM prompts.
        
        Args:
            activities_df (pd.DataFrame): Activities data
            
        Returns:
            str: Formatted activities string
        """
        if activities_df.empty:
            return "No activities found in the specified period."
        
        formatted_activities = []
        
        for _, activity in activities_df.iterrows():
            activity_str = f"""
Activity on {activity['activity_date']}:
- Sport: {activity['sport']} ({activity['subsport']})
- Distance: {activity['distance_in_km']} km
- Duration: {activity['elapsed_duration']}
- Pace: {activity['grade_adjusted_avg_pace_min_per_km']} min/km
- Avg Heart Rate: {activity['avg_heart_rate']} bpm
- Calories: {activity['calories_burnt']}
- Elevation: +{activity['total_ascent_in_meters']}m / -{activity['total_descent_in_meters']}m
- Training Effect: {activity['aerobic_training_effect_0_to_5']}/5
- Efficiency Index: {activity['running_efficiency_index'] if pd.notna(activity['running_efficiency_index']) else 'N/A'}
"""
            formatted_activities.append(activity_str)
        
        return "\n".join(formatted_activities)
    
    def build_weekly_analysis_prompt(self, activities_data: str, metrics: Dict[str, Any], days: int) -> str:
        """
        Build comprehensive prompt for weekly analysis.
        
        Args:
            activities_data (str): Formatted activities string
            metrics (Dict[str, Any]): Calculated metrics
            days (int): Number of days analyzed
            
        Returns:
            str: Complete analysis prompt
        """
        prompt = f"""
            Analyze the following {days}-day training period and provide comprehensive insights:

            TRAINING SUMMARY ({days} DAYS):
            - Total Activities: {metrics['total_activities']}
            - Total Distance: {metrics['total_distance_km']} km
            - Total Duration: {metrics['total_duration_hours']} hours
            - Average Heart Rate: {metrics['avg_heart_rate']} bpm
            - Total Calories: {metrics['total_calories']}
            - Total Elevation Gain: {metrics['total_ascent_m']} m
            - Sports Breakdown: {metrics['sports_breakdown']}
            - Average Training Effect: {metrics['avg_training_effect']}/5
            - Average Efficiency Index: {metrics['avg_efficiency_index']}

            DETAILED ACTIVITIES:
            {activities_data}

            Please provide analysis in the following structure:

            1. TRAINING LOAD ANALYSIS:
            - Overall training volume assessment
            - Intensity distribution analysis
            - Recovery patterns

            2. PERFORMANCE TRENDS:
            - Heart rate trends and zones
            - Pace/efficiency progression
            - Training effect analysis

            3. SPORT-SPECIFIC INSIGHTS:
            - Breakdown by activity type
            - Sport-specific recommendations

            4. RECOVERY & ADAPTATION:
            - Recovery indicators
            - Adaptation signals
            - Overtraining risk assessment

            5. RECOMMENDATIONS:
            - Immediate next steps
            - Training adjustments needed
            - Focus areas for improvement

            Provide specific, actionable insights based on the data above.
            """
        return prompt
    
    def analyze_weekly_trends(self, days: int = 7) -> str:
        """
        Perform comprehensive weekly analysis.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            str: Analysis results from LLM
        """
        # Get activities data
        activities_df = self.get_activities_data(days)
        
        # Calculate metrics
        metrics = self.calculate_weekly_metrics(activities_df)
        
        # Format activities for prompt
        activities_data = self.format_activities_for_prompt(activities_df)
        
        # Build analysis prompt
        prompt = self.build_weekly_analysis_prompt(activities_data, metrics, days)
        
        # Get analysis from LLM
        analysis = generate_response(prompt)
        
        return analysis
    
    def get_quick_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get quick summary metrics without LLM analysis.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            Dict[str, Any]: Summary metrics
        """
        activities_df = self.get_activities_data(days)
        metrics = self.calculate_weekly_metrics(activities_df)
        
        return {
            'period_days': days,
            'metrics': metrics,
            'activities_count': len(activities_df),
            'date_range': {
                'start': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'end': datetime.now().strftime('%Y-%m-%d')
            }
        }


# Convenience functions for easy access
def analyze_training_period(days: int = 7) -> str:
    """
    Analyze training data for the specified number of days.
    
    Args:
        days (int): Number of days to analyze (7, 10, 21, etc.)
        
    Returns:
        str: Comprehensive analysis from LLM
    """
    service = WeeklyAnalysisService()
    return service.analyze_weekly_trends(days)


def get_training_summary(days: int = 7) -> Dict[str, Any]:
    """
    Get quick training summary for the specified period.
    
    Args:
        days (int): Number of days to analyze
        
    Returns:
        Dict[str, Any]: Summary metrics
    """
    service = WeeklyAnalysisService()
    return service.get_quick_summary(days)


if __name__ == "__main__":
    # Test the service
    service = WeeklyAnalysisService()
    
    # Test with 7 days
    print("=== 7-Day Analysis ===")
    summary_7 = service.get_quick_summary(7)
    print(f"Activities: {summary_7['activities_count']}")
    print(f"Distance: {summary_7['metrics']['total_distance_km']} km")
    
    # Test with 21 days
    print("\n=== 21-Day Analysis ===")
    summary_21 = service.get_quick_summary(21)
    print(f"Activities: {summary_21['activities_count']}")
    print(f"Distance: {summary_21['metrics']['total_distance_km']} km")
