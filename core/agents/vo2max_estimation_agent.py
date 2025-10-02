"""
VO2 Max Estimation Agent

Estimates VO2 max and predicts race times using running data.
Uses validated formulas from exercise physiology research.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal
import math

logger = logging.getLogger(__name__)


@dataclass
class RaceTimePrediction:
    """Predicted race time for a specific distance"""
    distance_km: float
    distance_name: str
    predicted_time_seconds: int
    predicted_pace_per_km: str
    predicted_pace_per_mile: str
    confidence_level: str  # "high", "medium", "low"


@dataclass
class VO2MaxEstimate:
    """VO2 Max estimation and related metrics"""
    vo2_max: float  # ml/kg/min
    estimation_method: str
    vvo2_max_pace: Optional[str]  # Velocity at VO2 max (min/km)
    race_predictions: List[RaceTimePrediction]
    current_fitness_level: str
    recommendations: List[str]
    analysis_date: datetime
    data_quality_score: float  # 0-1 score


class VO2MaxEstimationAgent:
    """Agent for estimating VO2 max and predicting race times"""

    # VO2 Max categories (ml/kg/min) for runners
    VO2_CATEGORIES = {
        "elite": (65, 85),
        "excellent": (55, 65),
        "good": (45, 55),
        "average": (35, 45),
        "below_average": (25, 35)
    }

    # Standard race distances (km)
    RACE_DISTANCES = {
        "5K": 5.0,
        "10K": 10.0,
        "Half Marathon": 21.0975,
        "Marathon": 42.195
    }

    def __init__(self):
        logger.info("VO2MaxEstimationAgent initialized")

    def _parse_pace_string(self, pace_str: str) -> Optional[float]:
        """Parse pace string 'MM:SS' to seconds per km"""
        try:
            if ':' in pace_str:
                parts = pace_str.split(':')
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            else:
                return float(pace_str)
        except (ValueError, IndexError):
            return None

    def _seconds_to_pace_string(self, seconds: float) -> str:
        """Convert seconds to 'MM:SS' pace format"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def _meters_per_second_to_pace(self, mps: float, per_mile: bool = False) -> str:
        """Convert meters per second to pace string"""
        if mps <= 0:
            return "0:00"

        # Convert to seconds per km
        seconds_per_km = 1000 / mps

        if per_mile:
            # Convert to seconds per mile
            seconds_per_mile = seconds_per_km * 1.60934
            return self._seconds_to_pace_string(seconds_per_mile)
        else:
            return self._seconds_to_pace_string(seconds_per_km)

    def _estimate_vo2max_from_race_time(
        self,
        distance_meters: float,
        time_seconds: int
    ) -> Optional[float]:
        """
        Estimate VO2 max from race performance using Daniels & Gilbert formula
        VO2 = -4.60 + 0.182258 * v + 0.000104 * v^2
        where v is velocity in meters per minute
        """
        try:
            # Calculate velocity in meters per minute
            velocity_m_per_min = (distance_meters / time_seconds) * 60

            # Daniels formula for VO2 cost at a given velocity
            vo2 = -4.60 + 0.182258 * velocity_m_per_min + 0.000104 * (velocity_m_per_min ** 2)

            # Adjust based on race distance (longer races = lower % of VO2 max)
            distance_km = distance_meters / 1000
            if distance_km >= 40:  # Marathon
                vo2_max = vo2 / 0.85  # Running at ~85% VO2 max
            elif distance_km >= 20:  # Half marathon
                vo2_max = vo2 / 0.88
            elif distance_km >= 10:  # 10K
                vo2_max = vo2 / 0.92
            elif distance_km >= 5:  # 5K
                vo2_max = vo2 / 0.95
            else:  # Shorter distances
                vo2_max = vo2 / 0.98

            return max(20.0, min(85.0, vo2_max))  # Reasonable bounds

        except (ZeroDivisionError, ValueError):
            return None

    def _estimate_vo2max_from_power(self, watts_per_kg: float) -> float:
        """
        Estimate VO2 max from running power data
        Based on Stryd research: VO2 = 12.63 * P (for elite athletes)
        Adjusted for trained vs. untrained runners
        """
        # Elite formula: VO2 = 12.63 * watts/kg
        # Trained runners are ~4% more efficient
        vo2_max = 12.63 * watts_per_kg * 0.96

        return max(20.0, min(85.0, vo2_max))

    def _estimate_vo2max_from_heart_rate(
        self,
        activities: List[Dict[str, Any]]
    ) -> Optional[float]:
        """
        Estimate VO2 max from heart rate data using Uth-Sørensen-Overgaard-Pedersen formula
        VO2 max = 15.3 × (HRmax / HRrest)
        """
        try:
            # Find max heart rate from activities
            max_hrs = [a.get("max_heart_rate") for a in activities if a.get("max_heart_rate")]
            if not max_hrs:
                return None

            hr_max = max(max_hrs)

            # Estimate resting HR (typically 60-70 for runners, use 65)
            hr_rest = 65

            vo2_max = 15.3 * (hr_max / hr_rest)

            return max(20.0, min(85.0, vo2_max))

        except (ZeroDivisionError, ValueError):
            return None

    def _find_best_performances(
        self,
        activities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find best performances for standard distances"""
        best_performances = {}

        for activity in activities:
            distance = activity.get("distance")
            elapsed_time = activity.get("elapsed_time")

            if not distance or not elapsed_time:
                continue

            # Convert distance to meters if it's a Decimal
            if isinstance(distance, Decimal):
                distance_meters = float(distance)
            else:
                distance_meters = float(distance)

            # Check against standard distances (±10% tolerance)
            for race_name, race_km in self.RACE_DISTANCES.items():
                race_meters = race_km * 1000
                if 0.9 * race_meters <= distance_meters <= 1.1 * race_meters:
                    # This is close to a standard race distance
                    if race_name not in best_performances or elapsed_time < best_performances[race_name]["time"]:
                        best_performances[race_name] = {
                            "distance": distance_meters,
                            "time": elapsed_time,
                            "activity": activity
                        }

        return list(best_performances.values())

    def _predict_race_time_riegel(
        self,
        known_distance_m: float,
        known_time_s: int,
        target_distance_m: float
    ) -> int:
        """
        Predict race time using Riegel's formula
        T2 = T1 * (D2/D1)^1.06
        """
        fatigue_factor = 1.06  # Standard endurance factor

        predicted_time = known_time_s * ((target_distance_m / known_distance_m) ** fatigue_factor)

        return int(predicted_time)

    def _predict_race_time_vo2max(
        self,
        vo2_max: float,
        distance_km: float
    ) -> int:
        """
        Predict race time from VO2 max using reverse Daniels formula
        """
        # Determine race intensity (% of VO2 max)
        if distance_km >= 40:  # Marathon
            intensity = 0.85
        elif distance_km >= 20:  # Half marathon
            intensity = 0.88
        elif distance_km >= 10:  # 10K
            intensity = 0.92
        elif distance_km >= 5:  # 5K
            intensity = 0.95
        else:
            intensity = 0.98

        # VO2 at race pace
        vo2_at_pace = vo2_max * intensity

        # Reverse Daniels formula to find velocity
        # vo2 = -4.60 + 0.182258 * v + 0.000104 * v^2
        # Solve quadratic equation: 0.000104 * v^2 + 0.182258 * v + (-4.60 - vo2) = 0

        a = 0.000104
        b = 0.182258
        c = -4.60 - vo2_at_pace

        discriminant = b ** 2 - 4 * a * c
        if discriminant < 0:
            return 0

        velocity_m_per_min = (-b + math.sqrt(discriminant)) / (2 * a)

        # Convert to time for the race distance
        distance_meters = distance_km * 1000
        time_minutes = distance_meters / velocity_m_per_min
        time_seconds = int(time_minutes * 60)

        return time_seconds

    def _categorize_fitness(self, vo2_max: float) -> str:
        """Categorize fitness level based on VO2 max"""
        for category, (low, high) in self.VO2_CATEGORIES.items():
            if low <= vo2_max < high:
                return category
        return "average"

    def _calculate_confidence(
        self,
        estimation_method: str,
        recent_activities: int,
        has_power: bool,
        has_hr: bool
    ) -> float:
        """Calculate confidence score for VO2 max estimate"""
        confidence = 0.5  # Base confidence

        # Method quality
        if "race" in estimation_method.lower():
            confidence += 0.3
        elif "power" in estimation_method.lower() and has_power:
            confidence += 0.25
        elif "heart" in estimation_method.lower() and has_hr:
            confidence += 0.15

        # Data recency and volume
        if recent_activities >= 20:
            confidence += 0.15
        elif recent_activities >= 10:
            confidence += 0.10

        # Multiple data sources
        if has_power and has_hr:
            confidence += 0.05

        return min(1.0, confidence)

    def _generate_recommendations(
        self,
        vo2_max: float,
        fitness_level: str,
        vvo2_max_pace: Optional[str]
    ) -> List[str]:
        """Generate training recommendations based on VO2 max"""
        recommendations = []

        recommendations.append(
            f"Your estimated VO2 max of {vo2_max:.1f} ml/kg/min places you in the '{fitness_level}' category for runners."
        )

        if fitness_level == "elite":
            recommendations.append(
                "Maintain high-intensity interval training (HIIT) 1-2x per week to preserve VO2 max. "
                "Focus on race-specific workouts."
            )
        elif fitness_level == "excellent":
            recommendations.append(
                "Continue VO2 max intervals (3-5 min at 95-100% effort) weekly. "
                "You're approaching elite level with consistent training."
            )
        elif fitness_level == "good":
            recommendations.append(
                "Improve VO2 max with interval sessions: 5x1000m at 5K pace with 3min rest, "
                "or 4-6x800m at slightly faster than 5K pace."
            )
        else:
            recommendations.append(
                "Build aerobic base with easy runs (70-80% max HR) before adding high-intensity work. "
                "Gradual progression will improve VO2 max over 8-12 weeks."
            )

        if vvo2_max_pace:
            recommendations.append(
                f"Your vVO2 max pace is approximately {vvo2_max_pace}/km. "
                "This is the pace you can sustain for 4-8 minutes all-out. "
                "Use this for interval training targets."
            )

        recommendations.append(
            "VO2 max can improve 5-15% with 8-12 weeks of targeted interval training. "
            "Reassess monthly to track progress."
        )

        return recommendations

    async def estimate_vo2_max(
        self,
        activities: List[Dict[str, Any]]
    ) -> VO2MaxEstimate:
        """Estimate VO2 max from running activities and predict race times"""
        logger.info(f"Starting VO2 max estimation for {len(activities)} activities")

        if not activities:
            return self._create_fallback_estimate()

        # Find best performances
        best_performances = self._find_best_performances(activities)

        vo2_estimates = []
        estimation_methods = []

        # Method 1: Estimate from race performances
        for perf in best_performances:
            vo2 = self._estimate_vo2max_from_race_time(
                perf["distance"],
                perf["time"]
            )
            if vo2:
                vo2_estimates.append(vo2)
                estimation_methods.append("race_performance")

        # Method 2: Estimate from power data
        power_activities = [a for a in activities if a.get("average_watts")]
        if power_activities:
            avg_power = sum(a["average_watts"] for a in power_activities) / len(power_activities)
            # Estimate watts/kg (assuming average runner is 70kg, should ideally get from profile)
            watts_per_kg = avg_power / 70
            vo2 = self._estimate_vo2max_from_power(watts_per_kg)
            vo2_estimates.append(vo2)
            estimation_methods.append("power_data")

        # Method 3: Estimate from heart rate
        vo2_hr = self._estimate_vo2max_from_heart_rate(activities)
        if vo2_hr:
            vo2_estimates.append(vo2_hr)
            estimation_methods.append("heart_rate")

        # Calculate final VO2 max (weighted average, prefer race-based)
        if not vo2_estimates:
            return self._create_fallback_estimate()

        # Weight race-based estimates higher
        weights = [2.0 if "race" in method else 1.0 for method in estimation_methods]
        weighted_vo2 = sum(v * w for v, w in zip(vo2_estimates, weights)) / sum(weights)

        # Calculate vVO2 max pace (velocity at VO2 max)
        # Typically corresponds to ~3000-5000m race pace
        vvo2_max_pace = None
        if best_performances:
            # Use best 5K or similar
            best_5k = next((p for p in best_performances if 4500 <= p["distance"] <= 5500), None)
            if best_5k:
                velocity_mps = best_5k["distance"] / best_5k["time"]
                # vVO2 max is typically 5-10% faster than 5K pace
                vvo2_max_velocity = velocity_mps * 1.07
                vvo2_max_pace = self._meters_per_second_to_pace(vvo2_max_velocity)

        # Predict race times
        race_predictions = []
        primary_method = estimation_methods[0] if estimation_methods else "estimated"

        # Use best known performance for Riegel predictions
        if best_performances:
            best = max(best_performances, key=lambda p: p["distance"])

            for race_name, distance_km in self.RACE_DISTANCES.items():
                distance_m = distance_km * 1000

                # Predict using both methods and average
                predicted_riegel = self._predict_race_time_riegel(
                    best["distance"],
                    best["time"],
                    distance_m
                )

                predicted_vo2 = self._predict_race_time_vo2max(weighted_vo2, distance_km)

                # Average the two predictions
                predicted_time = int((predicted_riegel + predicted_vo2) / 2)

                # Calculate paces
                pace_per_km_sec = predicted_time / distance_km
                pace_per_mile_sec = pace_per_km_sec * 1.60934

                # Determine confidence
                confidence = "high" if abs(predicted_riegel - predicted_vo2) < 180 else "medium"

                race_predictions.append(RaceTimePrediction(
                    distance_km=distance_km,
                    distance_name=race_name,
                    predicted_time_seconds=predicted_time,
                    predicted_pace_per_km=self._seconds_to_pace_string(pace_per_km_sec),
                    predicted_pace_per_mile=self._seconds_to_pace_string(pace_per_mile_sec),
                    confidence_level=confidence
                ))

        # Categorize fitness
        fitness_level = self._categorize_fitness(weighted_vo2)

        # Generate recommendations
        recommendations = self._generate_recommendations(weighted_vo2, fitness_level, vvo2_max_pace)

        # Calculate data quality score
        has_power = any(a.get("average_watts") for a in activities)
        has_hr = any(a.get("average_heart_rate") for a in activities)
        data_quality = self._calculate_confidence(
            primary_method,
            len(activities),
            has_power,
            has_hr
        )

        logger.info(f"VO2 max estimation complete: {weighted_vo2:.1f} ml/kg/min ({fitness_level})")

        return VO2MaxEstimate(
            vo2_max=round(weighted_vo2, 1),
            estimation_method=primary_method,
            vvo2_max_pace=vvo2_max_pace,
            race_predictions=race_predictions,
            current_fitness_level=fitness_level,
            recommendations=recommendations,
            analysis_date=datetime.now(),
            data_quality_score=round(data_quality, 2)
        )

    def _create_fallback_estimate(self) -> VO2MaxEstimate:
        """Create fallback estimate when insufficient data"""
        logger.warning("Creating fallback VO2 max estimate")

        return VO2MaxEstimate(
            vo2_max=40.0,  # Average for recreational runners
            estimation_method="default",
            vvo2_max_pace=None,
            race_predictions=[],
            current_fitness_level="average",
            recommendations=[
                "Insufficient data for accurate VO2 max estimation. ",
                "Complete at least 3-4 runs at different paces to enable analysis.",
                "For best results, include a recent 5K or 10K race effort."
            ],
            analysis_date=datetime.now(),
            data_quality_score=0.3
        )
