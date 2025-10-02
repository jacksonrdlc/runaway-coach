"""
Training Load Agent

Calculates training stress, acute:chronic workload ratio (ACWR),
and provides recovery recommendations using validated sports science methods.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class RecoveryStatus(Enum):
    """Recovery status categories"""
    WELL_RECOVERED = "well_recovered"
    ADEQUATE = "adequate"
    FATIGUED = "fatigued"
    OVERREACHING = "overreaching"
    OVERTRAINED = "overtrained"


class TrainingLoadTrend(Enum):
    """Training load trend direction"""
    RAMPING_UP = "ramping_up"
    STEADY = "steady"
    TAPERING = "tapering"
    DETRAINING = "detraining"


@dataclass
class TrainingStressScore:
    """Training Stress Score for a single activity"""
    activity_id: str
    tss: float  # Training Stress Score
    duration_hours: float
    intensity_factor: float
    activity_date: datetime


@dataclass
class TrainingLoadAnalysis:
    """Complete training load analysis"""
    acute_load: float  # 7-day load
    chronic_load: float  # 28-day load
    acwr: float  # Acute:Chronic Workload Ratio
    weekly_tss: float  # Current week TSS
    total_volume_km: float  # Total distance last 7 days
    recovery_status: RecoveryStatus
    injury_risk_level: str  # "low", "moderate", "high", "very_high"
    training_trend: TrainingLoadTrend
    recommendations: List[str]
    daily_recommendations: Dict[str, str]  # Next 7 days
    analysis_date: datetime
    fitness_trend: str  # "improving", "maintaining", "declining"


class TrainingLoadAgent:
    """Agent for calculating training load and recovery needs"""

    # ACWR thresholds (based on Gabbett et al. research)
    ACWR_OPTIMAL_LOW = 0.8
    ACWR_OPTIMAL_HIGH = 1.3
    ACWR_HIGH_RISK = 1.5
    ACWR_VERY_HIGH_RISK = 1.8

    # TSS thresholds per week for different training phases
    TSS_EASY_WEEK = 200
    TSS_MODERATE_WEEK = 350
    TSS_HARD_WEEK = 500
    TSS_PEAK_WEEK = 700

    # Heart rate zones (% of max HR)
    HR_ZONES = {
        "zone1": (0.50, 0.60),  # Recovery
        "zone2": (0.60, 0.70),  # Easy/Aerobic
        "zone3": (0.70, 0.80),  # Tempo
        "zone4": (0.80, 0.90),  # Threshold
        "zone5": (0.90, 1.00),  # VO2 max/Anaerobic
    }

    def __init__(self):
        logger.info("TrainingLoadAgent initialized")

    def _calculate_intensity_factor(
        self,
        activity: Dict[str, Any],
        estimated_threshold_pace: Optional[float] = None
    ) -> float:
        """
        Calculate Intensity Factor (IF) for an activity
        IF = Normalized Pace / Threshold Pace
        Range: 0.5 (very easy) to 1.0+ (harder than threshold)
        """
        # Try to use heart rate data if available
        avg_hr = activity.get("average_heart_rate")
        max_hr = activity.get("max_heart_rate")

        if avg_hr and max_hr:
            # Estimate IF from HR percentage
            hr_percentage = avg_hr / max_hr if max_hr > 0 else 0.7

            # Convert HR % to approximate IF
            if hr_percentage < 0.65:  # Zone 1-2
                return 0.55
            elif hr_percentage < 0.75:  # Zone 2-3
                return 0.70
            elif hr_percentage < 0.85:  # Zone 3-4
                return 0.85
            else:  # Zone 4-5
                return 0.95

        # Fallback: estimate from pace if available
        avg_speed = activity.get("average_speed")
        if avg_speed and estimated_threshold_pace:
            if isinstance(avg_speed, Decimal):
                avg_speed = float(avg_speed)

            # Threshold pace is ~10K race pace
            if avg_speed > 0:
                normalized_pace = 1.0 / avg_speed
                if_estimate = estimated_threshold_pace / normalized_pace
                return max(0.5, min(1.2, if_estimate))

        # Default: assume moderate effort
        return 0.70

    def _calculate_tss(
        self,
        activity: Dict[str, Any],
        intensity_factor: float
    ) -> float:
        """
        Calculate Training Stress Score (TSS)
        TSS = (Duration * IF^2 * 100) / 3600
        """
        duration_seconds = activity.get("elapsed_time", 0)
        if isinstance(duration_seconds, (int, float, Decimal)):
            duration_hours = float(duration_seconds) / 3600
        else:
            duration_hours = 0

        tss = (duration_hours * (intensity_factor ** 2) * 100)

        return round(tss, 1)

    def _calculate_load_by_period(
        self,
        activities: List[Dict[str, Any]],
        days: int,
        reference_date: datetime
    ) -> float:
        """Calculate training load for a specific time period"""
        cutoff_date = reference_date - timedelta(days=days)

        period_activities = []
        for activity in activities:
            activity_date = activity.get("activity_date")
            if isinstance(activity_date, str):
                activity_date = datetime.fromisoformat(activity_date.replace('Z', '+00:00'))

            if activity_date and activity_date >= cutoff_date:
                period_activities.append(activity)

        # Calculate total TSS for period
        total_tss = 0
        for activity in period_activities:
            if_val = self._calculate_intensity_factor(activity)
            tss = self._calculate_tss(activity, if_val)
            total_tss += tss

        return round(total_tss, 1)

    def _calculate_acwr(self, acute_load: float, chronic_load: float) -> float:
        """Calculate Acute:Chronic Workload Ratio"""
        if chronic_load == 0:
            return 0.0

        acwr = acute_load / chronic_load
        return round(acwr, 2)

    def _assess_injury_risk(self, acwr: float) -> str:
        """Assess injury risk based on ACWR"""
        if acwr < self.ACWR_OPTIMAL_LOW:
            return "low"  # Detraining zone
        elif acwr <= self.ACWR_OPTIMAL_HIGH:
            return "low"  # Optimal training zone
        elif acwr <= self.ACWR_HIGH_RISK:
            return "moderate"  # Approaching high risk
        elif acwr <= self.ACWR_VERY_HIGH_RISK:
            return "high"  # High injury risk
        else:
            return "very_high"  # Very high injury risk

    def _determine_recovery_status(
        self,
        acwr: float,
        weekly_tss: float,
        recent_days: int
    ) -> RecoveryStatus:
        """Determine current recovery status"""
        # Very high ACWR = overtraining risk
        if acwr > self.ACWR_VERY_HIGH_RISK:
            return RecoveryStatus.OVERTRAINED

        # High ACWR with high volume = overreaching
        if acwr > self.ACWR_HIGH_RISK and weekly_tss > self.TSS_HARD_WEEK:
            return RecoveryStatus.OVERREACHING

        # Moderate ACWR with moderate volume = fatigued
        if acwr > self.ACWR_OPTIMAL_HIGH or weekly_tss > self.TSS_PEAK_WEEK:
            return RecoveryStatus.FATIGUED

        # Low ACWR or low volume = well recovered
        if acwr < self.ACWR_OPTIMAL_LOW or weekly_tss < self.TSS_EASY_WEEK:
            return RecoveryStatus.WELL_RECOVERED

        # Everything else = adequate
        return RecoveryStatus.ADEQUATE

    def _determine_training_trend(
        self,
        acute_load: float,
        chronic_load: float,
        acwr: float
    ) -> TrainingLoadTrend:
        """Determine current training trend"""
        if acwr > 1.2:
            return TrainingLoadTrend.RAMPING_UP
        elif acwr < 0.8:
            if chronic_load < 200:
                return TrainingLoadTrend.DETRAINING
            else:
                return TrainingLoadTrend.TAPERING
        else:
            return TrainingLoadTrend.STEADY

    def _assess_fitness_trend(
        self,
        chronic_load: float,
        load_4_weeks_ago: float
    ) -> str:
        """Assess fitness trend over longer period"""
        if load_4_weeks_ago == 0:
            return "insufficient_data"

        change_percent = ((chronic_load - load_4_weeks_ago) / load_4_weeks_ago) * 100

        if change_percent > 10:
            return "improving"
        elif change_percent < -10:
            return "declining"
        else:
            return "maintaining"

    def _generate_recommendations(
        self,
        acwr: float,
        recovery_status: RecoveryStatus,
        injury_risk: str,
        weekly_tss: float,
        training_trend: TrainingLoadTrend
    ) -> List[str]:
        """Generate training recommendations based on load analysis"""
        recommendations = []

        # ACWR-based recommendations
        if acwr > self.ACWR_VERY_HIGH_RISK:
            recommendations.append(
                f"⚠️ CRITICAL: ACWR is {acwr:.2f} (very high risk). "
                "Take 2-3 recovery days immediately. Reduce volume by 40-50% this week."
            )
        elif acwr > self.ACWR_HIGH_RISK:
            recommendations.append(
                f"⚠️ WARNING: ACWR is {acwr:.2f} (high injury risk). "
                "Add 1-2 rest days this week. Cap long run at 90 minutes."
            )
        elif acwr > self.ACWR_OPTIMAL_HIGH:
            recommendations.append(
                f"ACWR is {acwr:.2f} (above optimal). "
                "Maintain current volume but avoid intensity increases. "
                "Prioritize recovery runs for next 3-5 days."
            )
        elif acwr < self.ACWR_OPTIMAL_LOW:
            recommendations.append(
                f"ACWR is {acwr:.2f} (below optimal). "
                "Safe to increase training volume by 10-15% this week if feeling strong."
            )
        else:
            recommendations.append(
                f"✓ ACWR is {acwr:.2f} (optimal zone). "
                "Training load is well-managed. Continue current progression."
            )

        # Recovery status recommendations
        if recovery_status == RecoveryStatus.OVERTRAINED:
            recommendations.append(
                "Signs of overtraining detected. Consider taking 3-5 days complete rest "
                "or easy cross-training only. Monitor sleep quality and resting HR."
            )
        elif recovery_status == RecoveryStatus.OVERREACHING:
            recommendations.append(
                "Functional overreaching detected. Plan a recovery week with 50% reduced volume. "
                "This can lead to adaptation if followed by proper recovery."
            )
        elif recovery_status == RecoveryStatus.FATIGUED:
            recommendations.append(
                "Accumulated fatigue detected. Reduce intensity this week, focus on easy runs "
                "at <70% max HR. Sleep 8+ hours and prioritize nutrition."
            )

        # Weekly TSS recommendations
        if weekly_tss > self.TSS_PEAK_WEEK:
            recommendations.append(
                f"Weekly TSS of {weekly_tss:.0f} is very high. "
                "Plan a recovery week (40-50% reduction) within next 7-10 days."
            )
        elif weekly_tss < self.TSS_EASY_WEEK:
            recommendations.append(
                f"Weekly TSS of {weekly_tss:.0f} is low. "
                "Safe to add 1-2 quality workouts if no injury concerns."
            )

        # Trend-based recommendations
        if training_trend == TrainingLoadTrend.RAMPING_UP:
            recommendations.append(
                "Training volume is ramping up. Follow 3-weeks-up, 1-week-down pattern "
                "to allow adaptation and prevent overtraining."
            )
        elif training_trend == TrainingLoadTrend.DETRAINING:
            recommendations.append(
                "Training volume is declining. Fitness gains may be lost after 2-3 weeks "
                "of reduced training. Consider maintaining at least 2-3 runs per week."
            )

        # General recovery tips
        recommendations.append(
            "Recovery essentials: 7-9 hours sleep, protein within 30min post-run, "
            "foam rolling, and 1-2 complete rest days per week."
        )

        return recommendations

    def _generate_daily_recommendations(
        self,
        recovery_status: RecoveryStatus,
        acwr: float
    ) -> Dict[str, str]:
        """Generate daily workout recommendations for next 7 days"""
        daily_recs = {}

        if recovery_status in [RecoveryStatus.OVERTRAINED, RecoveryStatus.OVERREACHING]:
            # Aggressive recovery week
            daily_recs = {
                "Day 1": "Complete rest or 20min easy walk",
                "Day 2": "Complete rest or light yoga/stretching",
                "Day 3": "30min easy run (conversational pace, <70% max HR)",
                "Day 4": "Rest or 20min easy cross-training",
                "Day 5": "40min easy run (zone 2)",
                "Day 6": "Rest",
                "Day 7": "50min easy long run (comfortable pace)"
            }
        elif recovery_status == RecoveryStatus.FATIGUED:
            # Light recovery week
            daily_recs = {
                "Day 1": "30min easy run + stretching",
                "Day 2": "Rest or easy cross-training",
                "Day 3": "40min easy run (zone 2)",
                "Day 4": "30min easy run",
                "Day 5": "Rest",
                "Day 6": "45min moderate run (can include 10min tempo)",
                "Day 7": "60min easy long run"
            }
        elif recovery_status == RecoveryStatus.WELL_RECOVERED:
            # Can handle intensity
            daily_recs = {
                "Day 1": "40min easy run",
                "Day 2": "Interval workout: 6x800m at 5K pace (3min rest)",
                "Day 3": "30min recovery run",
                "Day 4": "50min tempo run (20min at threshold pace)",
                "Day 5": "Rest or 30min easy cross-training",
                "Day 6": "40min easy run",
                "Day 7": "90min long run (progressive pace)"
            }
        else:  # ADEQUATE
            # Balanced training
            daily_recs = {
                "Day 1": "40min easy run",
                "Day 2": "45min moderate run with 5x2min pickups",
                "Day 3": "30min recovery run",
                "Day 4": "50min tempo run (15min at threshold)",
                "Day 5": "Rest",
                "Day 6": "40min easy run",
                "Day 7": "75min long run (easy pace)"
            }

        return daily_recs

    async def analyze_training_load(
        self,
        activities: List[Dict[str, Any]]
    ) -> TrainingLoadAnalysis:
        """Analyze training load and provide recovery recommendations"""
        logger.info(f"Starting training load analysis for {len(activities)} activities")

        if not activities:
            return self._create_fallback_analysis()

        reference_date = datetime.now()

        # Calculate acute load (7 days)
        acute_load = self._calculate_load_by_period(activities, 7, reference_date)

        # Calculate chronic load (28 days)
        chronic_load = self._calculate_load_by_period(activities, 28, reference_date)

        # Calculate load from 4 weeks ago (for fitness trend)
        load_4_weeks_ago = self._calculate_load_by_period(
            activities, 28, reference_date - timedelta(days=28)
        )

        # Calculate ACWR
        acwr = self._calculate_acwr(acute_load, chronic_load)

        # Calculate weekly TSS (current week)
        weekly_tss = self._calculate_load_by_period(activities, 7, reference_date)

        # Calculate total volume (km) for last 7 days
        recent_activities = [
            a for a in activities
            if self._is_recent_activity(a, 7, reference_date)
        ]
        total_volume_km = sum(
            float(a.get("distance", 0)) / 1000 if a.get("distance") else 0
            for a in recent_activities
        )

        # Assess injury risk
        injury_risk = self._assess_injury_risk(acwr)

        # Determine recovery status
        recovery_status = self._determine_recovery_status(acwr, weekly_tss, 7)

        # Determine training trend
        training_trend = self._determine_training_trend(acute_load, chronic_load, acwr)

        # Assess fitness trend
        fitness_trend = self._assess_fitness_trend(chronic_load, load_4_weeks_ago)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            acwr, recovery_status, injury_risk, weekly_tss, training_trend
        )

        # Generate daily recommendations
        daily_recommendations = self._generate_daily_recommendations(recovery_status, acwr)

        logger.info(
            f"Training load analysis complete: ACWR={acwr:.2f}, "
            f"Recovery={recovery_status.value}, Risk={injury_risk}"
        )

        return TrainingLoadAnalysis(
            acute_load=acute_load,
            chronic_load=chronic_load,
            acwr=acwr,
            weekly_tss=weekly_tss,
            total_volume_km=round(total_volume_km, 1),
            recovery_status=recovery_status,
            injury_risk_level=injury_risk,
            training_trend=training_trend,
            recommendations=recommendations,
            daily_recommendations=daily_recommendations,
            analysis_date=reference_date,
            fitness_trend=fitness_trend
        )

    def _is_recent_activity(
        self,
        activity: Dict[str, Any],
        days: int,
        reference_date: datetime
    ) -> bool:
        """Check if activity is within the recent period"""
        activity_date = activity.get("activity_date")
        if isinstance(activity_date, str):
            activity_date = datetime.fromisoformat(activity_date.replace('Z', '+00:00'))

        if not activity_date:
            return False

        cutoff_date = reference_date - timedelta(days=days)
        return activity_date >= cutoff_date

    def _create_fallback_analysis(self) -> TrainingLoadAnalysis:
        """Create fallback analysis when insufficient data"""
        logger.warning("Creating fallback training load analysis")

        return TrainingLoadAnalysis(
            acute_load=0.0,
            chronic_load=0.0,
            acwr=0.0,
            weekly_tss=0.0,
            total_volume_km=0.0,
            recovery_status=RecoveryStatus.WELL_RECOVERED,
            injury_risk_level="low",
            training_trend=TrainingLoadTrend.STEADY,
            recommendations=[
                "Insufficient activity data for training load analysis.",
                "Track at least 4 weeks of training to enable ACWR calculations.",
                "Start with 3-4 easy runs per week and build gradually."
            ],
            daily_recommendations={
                "Day 1": "30min easy run",
                "Day 2": "Rest",
                "Day 3": "35min easy run",
                "Day 4": "Rest",
                "Day 5": "40min easy run",
                "Day 6": "Rest",
                "Day 7": "50min long run"
            },
            analysis_date=datetime.now(),
            fitness_trend="insufficient_data"
        )
