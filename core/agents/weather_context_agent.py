"""
Weather Context Agent

Analyzes performance in relation to weather conditions using Open-Meteo API.
Provides heat acclimation recommendations and optimal training time suggestions.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import httpx
from enum import Enum

logger = logging.getLogger(__name__)


class WeatherImpact(Enum):
    """Weather impact on performance"""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    SEVERE = "severe"


@dataclass
class WeatherConditions:
    """Weather conditions for a specific time/location"""
    temperature_celsius: float
    humidity_percent: float
    wind_speed_kmh: float
    precipitation_mm: float
    weather_code: int
    timestamp: datetime


@dataclass
class WeatherImpactAnalysis:
    """Analysis of weather impact on running performance"""
    average_temperature: float
    average_humidity: float
    heat_stress_runs: int  # Runs in >25°C or high humidity
    ideal_condition_runs: int  # Runs in 10-20°C
    weather_impact_score: WeatherImpact
    pace_degradation_estimate: float  # Seconds per mile slower due to weather
    recommendations: List[str]
    heat_acclimation_level: str  # "none", "developing", "well-acclimated"
    optimal_training_times: List[str]
    analysis_period: Dict[str, datetime]


class WeatherContextAgent:
    """Agent for analyzing weather impact on running performance"""

    # Open-Meteo API endpoint (free, no API key required)
    WEATHER_API_BASE = "https://archive-api.open-meteo.com/v1/archive"

    # Weather thresholds for running
    IDEAL_TEMP_LOW = 10  # Celsius
    IDEAL_TEMP_HIGH = 20  # Celsius
    HEAT_STRESS_TEMP = 25  # Celsius
    HIGH_HUMIDITY = 70  # Percent

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("WeatherContextAgent initialized with Open-Meteo API")

    async def _fetch_historical_weather(
        self,
        latitude: float,
        longitude: float,
        date: datetime
    ) -> Optional[WeatherConditions]:
        """Fetch historical weather data from Open-Meteo API"""
        try:
            # Format date for API
            date_str = date.strftime("%Y-%m-%d")

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": date_str,
                "end_date": date_str,
                "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
                "timezone": "auto"
            }

            response = await self.client.get(self.WEATHER_API_BASE, params=params)
            response.raise_for_status()
            data = response.json()

            # Get the hour that matches the activity time
            hour_index = date.hour
            hourly = data.get("hourly", {})

            if not hourly or len(hourly.get("temperature_2m", [])) <= hour_index:
                logger.warning(f"No weather data available for {date}")
                return None

            return WeatherConditions(
                temperature_celsius=hourly["temperature_2m"][hour_index],
                humidity_percent=hourly["relative_humidity_2m"][hour_index],
                wind_speed_kmh=hourly["wind_speed_10m"][hour_index],
                precipitation_mm=hourly["precipitation"][hour_index],
                weather_code=hourly["weather_code"][hour_index],
                timestamp=date
            )

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Failed to parse weather data: {e}")
            return None

    def _calculate_heat_index(self, temp_c: float, humidity: float) -> float:
        """Calculate heat index (feels-like temperature)"""
        # Convert to Fahrenheit for calculation
        temp_f = (temp_c * 9/5) + 32

        # Simplified heat index formula
        if temp_f < 80:
            return temp_c

        hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi -= 0.22475541 * temp_f * humidity
        hi -= 0.00683783 * temp_f * temp_f
        hi -= 0.05481717 * humidity * humidity
        hi += 0.00122874 * temp_f * temp_f * humidity
        hi += 0.00085282 * temp_f * humidity * humidity
        hi -= 0.00000199 * temp_f * temp_f * humidity * humidity

        # Convert back to Celsius
        return (hi - 32) * 5/9

    def _estimate_pace_degradation(
        self,
        temperature: float,
        humidity: float,
        heat_index: float
    ) -> float:
        """Estimate pace degradation in seconds per mile due to weather"""
        degradation = 0.0

        # Temperature impact
        if temperature > self.HEAT_STRESS_TEMP:
            # ~2-3% slower per degree above 25°C
            temp_excess = temperature - self.HEAT_STRESS_TEMP
            degradation += temp_excess * 4  # ~4 seconds per mile per degree

        # Humidity impact
        if humidity > self.HIGH_HUMIDITY:
            degradation += (humidity - self.HIGH_HUMIDITY) * 0.5

        # Heat index impact (combined effect)
        if heat_index > 30:
            degradation += (heat_index - 30) * 2

        return round(degradation, 1)

    def _determine_weather_impact(
        self,
        heat_stress_runs: int,
        total_runs: int,
        avg_temp: float
    ) -> WeatherImpact:
        """Determine overall weather impact level"""
        if total_runs == 0:
            return WeatherImpact.MINIMAL

        heat_ratio = heat_stress_runs / total_runs

        if heat_ratio > 0.5 or avg_temp > 28:
            return WeatherImpact.SEVERE
        elif heat_ratio > 0.3 or avg_temp > 25:
            return WeatherImpact.SIGNIFICANT
        elif heat_ratio > 0.15 or avg_temp > 22:
            return WeatherImpact.MODERATE
        else:
            return WeatherImpact.MINIMAL

    def _assess_heat_acclimation(
        self,
        heat_stress_runs: int,
        total_runs: int
    ) -> str:
        """Assess athlete's heat acclimation level"""
        if total_runs == 0:
            return "none"

        heat_ratio = heat_stress_runs / total_runs

        # Well-acclimated: regularly running in heat (>40% of runs)
        if heat_ratio > 0.4 and heat_stress_runs >= 8:
            return "well-acclimated"
        # Developing: some heat exposure (15-40% of runs)
        elif heat_ratio > 0.15 and heat_stress_runs >= 4:
            return "developing"
        else:
            return "none"

    def _generate_recommendations(
        self,
        weather_impact: WeatherImpact,
        heat_acclimation: str,
        avg_temp: float,
        avg_humidity: float,
        pace_degradation: float
    ) -> List[str]:
        """Generate weather-specific training recommendations"""
        recommendations = []

        # Temperature-based recommendations
        if avg_temp > self.HEAT_STRESS_TEMP:
            recommendations.append(
                f"Average training temperature ({avg_temp:.1f}°C) is above ideal. "
                f"Expect {pace_degradation:.0f}s/mile slower pace in heat."
            )

            if heat_acclimation == "none":
                recommendations.append(
                    "Build heat tolerance gradually: start with shorter, easier runs "
                    "in warm conditions before attempting long/hard efforts."
                )
            elif heat_acclimation == "developing":
                recommendations.append(
                    "Continue heat acclimation with 3-4 runs per week in warm conditions. "
                    "Full adaptation takes 10-14 days."
                )

            recommendations.append(
                "Hydrate 16-20oz per hour in heat. Consider electrolyte supplementation "
                "for runs >60 minutes."
            )

        # Humidity recommendations
        if avg_humidity > self.HIGH_HUMIDITY:
            recommendations.append(
                f"High humidity ({avg_humidity:.0f}%) impairs cooling. "
                "Reduce pace by 10-20s/mile on humid days."
            )

        # Optimal timing
        if avg_temp > 22:
            recommendations.append(
                "Train early morning (5-7am) or evening (7-9pm) to avoid peak heat. "
                "Temperature can be 5-10°C cooler during these windows."
            )

        # Ideal conditions
        if self.IDEAL_TEMP_LOW <= avg_temp <= self.IDEAL_TEMP_HIGH:
            recommendations.append(
                f"Excellent training conditions ({avg_temp:.1f}°C)! "
                "Ideal for tempo runs and interval workouts."
            )

        # Cold weather
        if avg_temp < 5:
            recommendations.append(
                "Layer clothing for cold weather: base layer, insulating layer, "
                "wind-breaking outer layer. Warm up gradually."
            )

        return recommendations

    async def analyze_weather_impact(
        self,
        activities: List[Dict[str, Any]]
    ) -> WeatherImpactAnalysis:
        """Analyze weather impact on running performance"""
        logger.info(f"Starting weather impact analysis for {len(activities)} activities")

        # Filter activities with location data
        activities_with_location = [
            a for a in activities
            if a.get("start_latitude") and a.get("start_longitude")
        ]

        if not activities_with_location:
            logger.warning("No activities with location data for weather analysis")
            return self._create_fallback_analysis(activities)

        # Fetch weather data for each activity
        weather_data = []
        for activity in activities_with_location[:30]:  # Limit to recent 30 to avoid rate limits
            if not activity.get("activity_date"):
                continue

            # Parse activity date
            if isinstance(activity["activity_date"], str):
                activity_date = datetime.fromisoformat(activity["activity_date"].replace('Z', '+00:00'))
            else:
                activity_date = activity["activity_date"]

            weather = await self._fetch_historical_weather(
                latitude=float(activity["start_latitude"]),
                longitude=float(activity["start_longitude"]),
                date=activity_date
            )

            if weather:
                weather_data.append(weather)

        if not weather_data:
            logger.warning("Could not fetch weather data for activities")
            return self._create_fallback_analysis(activities)

        # Calculate metrics
        avg_temp = sum(w.temperature_celsius for w in weather_data) / len(weather_data)
        avg_humidity = sum(w.humidity_percent for w in weather_data) / len(weather_data)

        heat_stress_runs = sum(
            1 for w in weather_data
            if w.temperature_celsius > self.HEAT_STRESS_TEMP or w.humidity_percent > self.HIGH_HUMIDITY
        )

        ideal_condition_runs = sum(
            1 for w in weather_data
            if self.IDEAL_TEMP_LOW <= w.temperature_celsius <= self.IDEAL_TEMP_HIGH
        )

        # Calculate heat index and pace degradation
        avg_heat_index = self._calculate_heat_index(avg_temp, avg_humidity)
        pace_degradation = self._estimate_pace_degradation(avg_temp, avg_humidity, avg_heat_index)

        # Determine impact level
        weather_impact = self._determine_weather_impact(heat_stress_runs, len(weather_data), avg_temp)

        # Assess heat acclimation
        heat_acclimation = self._assess_heat_acclimation(heat_stress_runs, len(weather_data))

        # Generate recommendations
        recommendations = self._generate_recommendations(
            weather_impact,
            heat_acclimation,
            avg_temp,
            avg_humidity,
            pace_degradation
        )

        # Determine optimal training times
        optimal_times = self._get_optimal_training_times(avg_temp)

        logger.info(f"Weather analysis complete: {weather_impact.value} impact, {len(recommendations)} recommendations")

        return WeatherImpactAnalysis(
            average_temperature=round(avg_temp, 1),
            average_humidity=round(avg_humidity, 1),
            heat_stress_runs=heat_stress_runs,
            ideal_condition_runs=ideal_condition_runs,
            weather_impact_score=weather_impact,
            pace_degradation_estimate=pace_degradation,
            recommendations=recommendations,
            heat_acclimation_level=heat_acclimation,
            optimal_training_times=optimal_times,
            analysis_period={
                "start": weather_data[-1].timestamp,
                "end": weather_data[0].timestamp,
                "total_activities_analyzed": len(weather_data)
            }
        )

    def _get_optimal_training_times(self, avg_temp: float) -> List[str]:
        """Get optimal training time windows based on temperature"""
        if avg_temp > 25:
            return ["5:00-7:00 AM (coolest)", "8:00-10:00 PM (evening cool-down)"]
        elif avg_temp > 20:
            return ["6:00-8:00 AM (mild)", "7:00-9:00 PM (comfortable)"]
        else:
            return ["10:00 AM-4:00 PM (warmest)", "Any time (good conditions)"]

    def _create_fallback_analysis(self, activities: List[Dict[str, Any]]) -> WeatherImpactAnalysis:
        """Create fallback analysis when weather data unavailable"""
        logger.warning("Creating fallback weather analysis")

        # Use weather data from activities if available
        temps = [a.get("average_temperature") for a in activities if a.get("average_temperature")]
        humidity = [a.get("humidity") for a in activities if a.get("humidity")]

        avg_temp = sum(float(t) for t in temps) / len(temps) if temps else 15.0
        avg_humidity = sum(float(h) for h in humidity) / len(humidity) if humidity else 60.0

        return WeatherImpactAnalysis(
            average_temperature=round(avg_temp, 1),
            average_humidity=round(avg_humidity, 1),
            heat_stress_runs=0,
            ideal_condition_runs=0,
            weather_impact_score=WeatherImpact.MINIMAL,
            pace_degradation_estimate=0.0,
            recommendations=[
                "Weather data unavailable for detailed analysis. "
                "General tip: Train in 10-20°C for optimal performance."
            ],
            heat_acclimation_level="unknown",
            optimal_training_times=["6:00-8:00 AM", "7:00-9:00 PM"],
            analysis_period={
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now(),
                "total_activities_analyzed": 0
            }
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
