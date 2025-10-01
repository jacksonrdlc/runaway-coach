from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from decimal import Decimal

from models.strava import EnhancedActivity, Athlete, AthleteStats

logger = logging.getLogger(__name__)

class PerformanceTrend(Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"

@dataclass
class PerformanceMetrics:
    weekly_mileage: float
    recent_trend: PerformanceTrend
    consistency: float
    avg_pace: str

@dataclass
class PerformanceAnalysis:
    metrics: PerformanceMetrics
    strengths: List[str]
    recommendations: List[str]
    analysis_date: str

class PerformanceAnalysisAgent:
    def __init__(self):
        # Load .env file explicitly
        load_dotenv()
        
        self.client = None
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = AsyncAnthropic(api_key=api_key)
        except Exception as e:
            logger.error(f"Anthropic client initialization failed: {e}")
        logger.info("PerformanceAnalysisAgent initialized")
    
    async def analyze_performance(self, activities_data: List[Dict[str, Any]]) -> PerformanceAnalysis:
        """Analyze performance trends from activities data using GenAI (legacy interface)"""
        try:
            # Calculate basic metrics from activities data
            metrics = self._calculate_basic_metrics(activities_data)

            # Generate AI-powered analysis and recommendations
            if self.client:
                ai_analysis = await self._generate_ai_analysis(activities_data, metrics)
                strengths = ai_analysis.get("strengths", [])
                recommendations = ai_analysis.get("recommendations", [])
            else:
                logger.warning("Anthropic client not available, using fallback recommendations")
                strengths, recommendations = self._get_fallback_analysis(metrics)

            analysis = PerformanceAnalysis(
                metrics=metrics,
                strengths=strengths,
                recommendations=recommendations,
                analysis_date=datetime.now().isoformat()
            )

            logger.info(f"Performance analysis completed for {len(activities_data)} activities")
            return analysis

        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            # Fall back to basic analysis if AI fails
            return self._get_fallback_performance_analysis(activities_data)

    async def analyze_performance_enhanced(
        self,
        athlete: Athlete,
        stats: AthleteStats,
        activities: List[EnhancedActivity]
    ) -> PerformanceAnalysis:
        """Enhanced performance analysis with full Strava data context"""
        try:
            # Calculate enhanced metrics
            metrics = self._calculate_enhanced_metrics(activities)

            # Generate AI-powered analysis with full context
            if self.client:
                ai_analysis = await self._generate_enhanced_ai_analysis(
                    athlete, stats, activities, metrics
                )
                strengths = ai_analysis.get("strengths", [])
                recommendations = ai_analysis.get("recommendations", [])
            else:
                logger.warning("Anthropic client not available, using fallback")
                strengths, recommendations = self._get_fallback_analysis(metrics)

            analysis = PerformanceAnalysis(
                metrics=metrics,
                strengths=strengths,
                recommendations=recommendations,
                analysis_date=datetime.now().isoformat()
            )

            logger.info(f"Enhanced performance analysis completed for athlete {athlete.id}")
            return analysis

        except Exception as e:
            logger.error(f"Enhanced performance analysis failed: {str(e)}")
            # Fall back to basic metrics
            metrics = self._calculate_enhanced_metrics(activities)
            strengths, recommendations = self._get_fallback_analysis(metrics)
            return PerformanceAnalysis(
                metrics=metrics,
                strengths=strengths,
                recommendations=recommendations,
                analysis_date=datetime.now().isoformat()
            )
    
    def _calculate_basic_metrics(self, activities_data: List[Dict[str, Any]]) -> PerformanceMetrics:
        """Calculate basic performance metrics from activities data"""
        if not activities_data:
            return PerformanceMetrics(
                weekly_mileage=0.0,
                recent_trend=PerformanceTrend.STABLE,
                consistency=0.0,
                avg_pace="N/A"
            )
        
        # Calculate weekly mileage (assuming activities are from recent weeks)
        total_distance = sum(activity.get('distance', 0) for activity in activities_data)
        weekly_mileage = (total_distance / 1000) * 0.621371  # Convert to miles
        
        # Calculate average pace
        total_time = sum(activity.get('elapsed_time', 0) for activity in activities_data)
        avg_pace = f"{int(total_time // 60 // len(activities_data))}:{int((total_time % 60) // len(activities_data)):02d}" if total_time > 0 else "N/A"
        
        # Simple trend analysis based on recent vs older activities
        recent_trend = PerformanceTrend.STABLE
        if len(activities_data) >= 4:
            recent_avg = sum(activity.get('distance', 0) for activity in activities_data[:2]) / 2
            older_avg = sum(activity.get('distance', 0) for activity in activities_data[-2:]) / 2
            if recent_avg > older_avg * 1.1:
                recent_trend = PerformanceTrend.IMPROVING
            elif recent_avg < older_avg * 0.9:
                recent_trend = PerformanceTrend.DECLINING
        
        # Calculate consistency (percentage of planned vs actual runs)
        consistency = min(1.0, len(activities_data) / 7)  # Assume 7 runs per week is ideal
        
        return PerformanceMetrics(
            weekly_mileage=weekly_mileage,
            recent_trend=recent_trend,
            consistency=consistency,
            avg_pace=avg_pace
        )
    
    async def _generate_ai_analysis(self, activities_data: List[Dict[str, Any]], metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Generate AI-powered performance analysis and recommendations"""
        try:
            # Prepare activity summary for AI
            activity_summary = self._prepare_activity_summary(activities_data)
            
            prompt = f"""
            As an expert running coach, analyze this runner's performance data and provide personalized insights:

            PERFORMANCE METRICS:
            - Weekly mileage: {metrics.weekly_mileage:.1f} miles
            - Recent trend: {metrics.recent_trend.value}
            - Consistency: {metrics.consistency:.1%}
            - Average pace: {metrics.avg_pace}

            RECENT ACTIVITIES:
            {activity_summary}

            Please provide a JSON response with:
            1. "strengths": List of 3-4 specific strengths based on the data
            2. "recommendations": List of 3-5 personalized, actionable recommendations

            Focus on:
            - Specific insights from their actual performance data
            - Actionable training adjustments
            - Addressing any concerning trends
            - Building on their strengths
            - Personalized advice based on their current fitness level
            - Use MILES for all distance measurements (not kilometers)
            - Provide specific, measurable recommendations

            Respond in JSON format only.
            """
            
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the AI response
            import json
            ai_content = response.content[0].text
            
            # Extract JSON from the response
            try:
                # Try to find JSON in the response
                start = ai_content.find('{')
                end = ai_content.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = ai_content[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            # If JSON parsing fails, fall back to basic parsing
            return self._parse_ai_response_fallback(ai_content)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._get_fallback_analysis(metrics)
    
    def _prepare_activity_summary(self, activities_data: List[Dict[str, Any]]) -> str:
        """Prepare a summary of activities for AI analysis"""
        if not activities_data:
            return "No recent activities available"
        
        summary_lines = []
        for i, activity in enumerate(activities_data[:10]):  # Limit to 10 most recent
            distance = (activity.get('distance', 0) / 1000) * 0.621371  # Convert to miles
            duration = activity.get('elapsed_time', 0)
            name = activity.get('name', f'Run {i+1}')
            
            duration_str = f"{duration//60:.0f}:{duration%60:02.0f}" if duration > 0 else "N/A"
            summary_lines.append(f"- {name}: {distance:.1f} miles in {duration_str}")
        
        return "\n".join(summary_lines)
    
    def _parse_ai_response_fallback(self, ai_content: str) -> Dict[str, Any]:
        """Fallback parsing if JSON parsing fails"""
        lines = ai_content.split('\n')
        strengths = []
        recommendations = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if 'strength' in line.lower():
                current_section = 'strengths'
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-• ').strip()
                if item and current_section == 'strengths':
                    strengths.append(item)
                elif item and current_section == 'recommendations':
                    recommendations.append(item)
        
        return {
            "strengths": strengths[:4] if strengths else ["Consistent training approach"],
            "recommendations": recommendations[:5] if recommendations else ["Continue current training plan"]
        }
    
    def _get_fallback_analysis(self, metrics: PerformanceMetrics) -> tuple:
        """Fallback analysis when AI is not available"""
        strengths = []
        recommendations = []
        
        # Generate strengths based on metrics
        if metrics.consistency > 0.7:
            strengths.append("Excellent training consistency")
        if metrics.recent_trend == PerformanceTrend.IMPROVING:
            strengths.append("Strong performance progression")
        if metrics.weekly_mileage > 12:  # ~20km converted to miles
            strengths.append("Good weekly mileage base")
        
        # Generate recommendations based on metrics
        if metrics.consistency < 0.6:
            recommendations.append("Focus on improving training consistency")
        if metrics.recent_trend == PerformanceTrend.DECLINING:
            recommendations.append("Consider reducing intensity and focusing on recovery")
        if metrics.weekly_mileage < 9:  # ~15km converted to miles
            recommendations.append("Gradually increase weekly mileage")
        
        return strengths, recommendations
    
    def _get_fallback_performance_analysis(self, activities_data: List[Dict[str, Any]]) -> PerformanceAnalysis:
        """Complete fallback analysis when everything fails"""
        metrics = self._calculate_basic_metrics(activities_data)
        strengths, recommendations = self._get_fallback_analysis(metrics)

        return PerformanceAnalysis(
            metrics=metrics,
            strengths=strengths if strengths else ["Maintaining regular training schedule"],
            recommendations=recommendations if recommendations else ["Continue current training approach"],
            analysis_date=datetime.now().isoformat()
        )

    # =====================================
    # Enhanced Analysis Methods
    # =====================================

    def _calculate_enhanced_metrics(self, activities: List[EnhancedActivity]) -> PerformanceMetrics:
        """Calculate metrics from EnhancedActivity objects"""
        if not activities:
            return PerformanceMetrics(
                weekly_mileage=0.0,
                recent_trend=PerformanceTrend.STABLE,
                consistency=0.0,
                avg_pace="N/A"
            )

        # Calculate weekly mileage
        total_distance_meters = sum(float(a.distance) for a in activities)
        weekly_mileage = (total_distance_meters / 1000) * 0.621371  # Convert to miles

        # Calculate average pace
        total_time = sum(a.moving_time for a in activities)
        if total_time > 0 and len(activities) > 0:
            avg_time_per_activity = total_time / len(activities)
            pace_minutes = int(avg_time_per_activity // 60)
            pace_seconds = int(avg_time_per_activity % 60)
            avg_pace = f"{pace_minutes}:{pace_seconds:02d}"
        else:
            avg_pace = "N/A"

        # Enhanced trend analysis using distance + pace
        recent_trend = PerformanceTrend.STABLE
        if len(activities) >= 4:
            recent_avg_distance = sum(float(a.distance) for a in activities[:2]) / 2
            older_avg_distance = sum(float(a.distance) for a in activities[-2:]) / 2
            if recent_avg_distance > older_avg_distance * 1.1:
                recent_trend = PerformanceTrend.IMPROVING
            elif recent_avg_distance < older_avg_distance * 0.9:
                recent_trend = PerformanceTrend.DECLINING

        # Calculate consistency
        consistency = min(1.0, len(activities) / 7)  # Assume 7 runs per week is ideal

        return PerformanceMetrics(
            weekly_mileage=weekly_mileage,
            recent_trend=recent_trend,
            consistency=consistency,
            avg_pace=avg_pace
        )

    async def _generate_enhanced_ai_analysis(
        self,
        athlete: Athlete,
        stats: AthleteStats,
        activities: List[EnhancedActivity],
        metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """Generate comprehensive AI analysis with full context"""
        try:
            # Prepare comprehensive context
            activity_summary = self._format_enhanced_activities(activities[:10])
            weather_insights = self._analyze_weather_impact(activities)
            hr_analysis = self._analyze_hr_zones(activities)
            elevation_analysis = self._analyze_elevation_patterns(activities)
            cadence_analysis = self._analyze_cadence(activities)

            prompt = f"""
As an expert running coach, analyze this runner's performance with comprehensive data:

ATHLETE PROFILE:
- Name: {athlete.first_name} {athlete.last_name}
- Location: {athlete.city}, {athlete.state}, {athlete.country}
- Weight: {athlete.weight} kg

LIFETIME STATISTICS:
- Total Activities: {stats.count}
- Total Distance: {float(stats.distance) / 1000:.1f} km ({(float(stats.distance) / 1000) * 0.621371:.1f} miles)
- Total Moving Time: {stats.moving_time / 3600:.1f} hours
- Total Elevation Gain: {float(stats.elevation_gain):.0f} meters
- YTD Distance: {float(stats.ytd_distance) / 1000:.1f} km ({(float(stats.ytd_distance) / 1000) * 0.621371:.1f} miles)
- Achievements: {stats.achievement_count}

CURRENT PERFORMANCE METRICS:
- Weekly Mileage: {metrics.weekly_mileage:.1f} miles
- Recent Trend: {metrics.recent_trend.value}
- Consistency: {metrics.consistency:.1%}
- Average Pace: {metrics.avg_pace}

RECENT ACTIVITIES (last 10):
{activity_summary}

WEATHER IMPACT ANALYSIS:
{weather_insights}

HEART RATE ZONE ANALYSIS:
{hr_analysis}

ELEVATION EFFICIENCY:
{elevation_analysis}

CADENCE ANALYSIS:
{cadence_analysis}

Please provide a JSON response with:
1. "strengths": List of 3-5 data-driven strengths with specific evidence
2. "recommendations": List of 3-5 actionable recommendations based on the data
3. "weather_insights": How weather conditions affect their performance
4. "form_insights": Analysis of cadence, HR zones, and running efficiency
5. "trend_analysis": Specific trend insights with supporting data

Focus on:
- Concrete insights from actual performance data
- Weather-adjusted performance expectations
- Heart rate zone optimization
- Cadence and form improvements
- Elevation efficiency
- Use MILES for all distance measurements
- Provide specific, measurable recommendations

Respond in JSON format only.
"""

            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse AI response
            import json
            ai_content = response.content[0].text

            try:
                start = ai_content.find('{')
                end = ai_content.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = ai_content[start:end]
                    return json.loads(json_str)
            except:
                pass

            # Fallback parsing
            return self._parse_ai_response_fallback(ai_content)

        except Exception as e:
            logger.error(f"Enhanced AI analysis failed: {str(e)}")
            return self._get_fallback_analysis(metrics)

    def _format_enhanced_activities(self, activities: List[EnhancedActivity]) -> str:
        """Format enhanced activities for AI analysis"""
        if not activities:
            return "No recent activities available"

        summary_lines = []
        for i, activity in enumerate(activities):
            distance_miles = (float(activity.distance) / 1000) * 0.621371
            duration_str = f"{activity.moving_time//60:.0f}:{activity.moving_time%60:02.0f}"

            # Add weather context if available
            weather_str = f" (Weather: {activity.weather_condition}" if activity.weather_condition else ""
            if activity.average_temperature:
                weather_str += f", {float(activity.average_temperature)}°C"
            if activity.humidity:
                weather_str += f", {float(activity.humidity)}% humidity"
            if weather_str:
                weather_str += ")"

            # Add elevation
            elevation_str = f", +{float(activity.elevation_gain):.0f}m" if activity.elevation_gain else ""

            # Add HR if available
            hr_str = f", HR: {activity.average_heart_rate} bpm" if activity.average_heart_rate else ""

            summary_lines.append(
                f"- {activity.name}: {distance_miles:.1f} miles in {duration_str}"
                f"{elevation_str}{hr_str}{weather_str}"
            )

        return "\n".join(summary_lines)

    def _analyze_weather_impact(self, activities: List[EnhancedActivity]) -> str:
        """Analyze how weather conditions affect performance"""
        weather_activities = [a for a in activities if a.weather_condition]
        if not weather_activities:
            return "No weather data available"

        # Group by weather condition
        weather_groups: Dict[str, List[float]] = {}
        for activity in weather_activities:
            condition = activity.weather_condition or "unknown"
            if condition not in weather_groups:
                weather_groups[condition] = []
            # Calculate pace (min/mile)
            if activity.distance and activity.moving_time:
                miles = (float(activity.distance) / 1000) * 0.621371
                pace_min_per_mile = activity.moving_time / 60 / miles if miles > 0 else 0
                weather_groups[condition].append(pace_min_per_mile)

        # Summarize
        summary_lines = []
        for condition, paces in weather_groups.items():
            if paces:
                avg_pace = sum(paces) / len(paces)
                summary_lines.append(f"- {condition.title()}: Avg pace {int(avg_pace)}:{int((avg_pace % 1) * 60):02d}/mile ({len(paces)} runs)")

        return "\n".join(summary_lines) if summary_lines else "Insufficient weather data for analysis"

    def _analyze_hr_zones(self, activities: List[EnhancedActivity]) -> str:
        """Analyze heart rate zone distribution"""
        hr_activities = [a for a in activities if a.average_heart_rate]
        if not hr_activities:
            return "No heart rate data available"

        # Calculate statistics
        hr_values = [a.average_heart_rate for a in hr_activities if a.average_heart_rate]
        avg_hr = sum(hr_values) / len(hr_values)
        max_observed = max(hr_values)

        # Estimate zones (rough approximation)
        zone_2_count = sum(1 for hr in hr_values if 0.6 * max_observed <= hr <= 0.7 * max_observed)
        zone_3_count = sum(1 for hr in hr_values if 0.7 * max_observed < hr <= 0.8 * max_observed)
        zone_4_count = sum(1 for hr in hr_values if hr > 0.8 * max_observed)

        return f"""
- Average HR: {avg_hr:.0f} bpm
- Max Observed: {max_observed} bpm
- Zone 2 (Aerobic) runs: {zone_2_count}
- Zone 3 (Tempo) runs: {zone_3_count}
- Zone 4+ (Threshold/VO2) runs: {zone_4_count}
        """.strip()

    def _analyze_elevation_patterns(self, activities: List[EnhancedActivity]) -> str:
        """Analyze elevation gain patterns and efficiency"""
        elevation_activities = [a for a in activities if a.elevation_gain]
        if not elevation_activities:
            return "No elevation data available"

        total_gain = sum(float(a.elevation_gain) for a in elevation_activities if a.elevation_gain)
        avg_gain_per_run = total_gain / len(elevation_activities)

        # Find hilly vs flat runs
        hilly_runs = [a for a in elevation_activities if a.elevation_gain and float(a.elevation_gain) > 100]
        flat_runs = [a for a in elevation_activities if a.elevation_gain and float(a.elevation_gain) <= 100]

        return f"""
- Total elevation gain: {total_gain:.0f} meters across {len(elevation_activities)} runs
- Average gain per run: {avg_gain_per_run:.0f} meters
- Hilly runs (>100m gain): {len(hilly_runs)}
- Flat runs (≤100m gain): {len(flat_runs)}
        """.strip()

    def _analyze_cadence(self, activities: List[EnhancedActivity]) -> str:
        """Analyze running cadence patterns"""
        cadence_activities = [a for a in activities if a.average_cadence]
        if not cadence_activities:
            return "No cadence data available"

        cadences = [a.average_cadence for a in cadence_activities if a.average_cadence]
        avg_cadence = sum(cadences) / len(cadences)
        min_cadence = min(cadences)
        max_cadence = max(cadences)

        # Assess cadence quality (optimal is typically 170-180 spm)
        quality = "optimal" if 170 <= avg_cadence <= 180 else "needs improvement"
        recommendation = ""
        if avg_cadence < 170:
            recommendation = " - Consider increasing cadence for better efficiency"
        elif avg_cadence > 180:
            recommendation = " - Very high cadence, ensure you're not overstriding"

        return f"""
- Average cadence: {avg_cadence:.0f} spm ({quality}){recommendation}
- Range: {min_cadence}-{max_cadence} spm
- Activities with cadence data: {len(cadence_activities)}
        """.strip()