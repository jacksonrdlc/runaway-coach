# iOS App Feature Specifications - Quick Wins Agents

## Overview

This document provides detailed specifications for building iOS views to display the Quick Wins agent data. Each section includes the API endpoint, response structure, and recommended UI components.

---

## 1. Weather Impact Analysis

### API Endpoint
```
GET /quick-wins/weather-impact?limit=30
```

### Response Structure
```json
{
  "success": true,
  "analysis": {
    "average_temperature_celsius": 24.5,
    "average_humidity_percent": 68.2,
    "heat_stress_runs": 12,
    "ideal_condition_runs": 8,
    "weather_impact_score": "moderate",
    "pace_degradation_seconds_per_mile": 15.2,
    "heat_acclimation_level": "developing",
    "optimal_training_times": ["5:00-7:00 AM", "8:00-10:00 PM"],
    "recommendations": [
      "Average training temperature (24.5°C) is above ideal...",
      "High humidity (68.2%) impairs cooling..."
    ],
    "analysis_period": {
      "start": "2025-09-01T06:30:00Z",
      "end": "2025-09-30T18:45:00Z",
      "total_activities_analyzed": 28
    }
  }
}
```

### iOS View Components

#### **Hero Card - Weather Impact Summary**
```swift
VStack(alignment: .leading, spacing: 12) {
    // Header
    HStack {
        Image(systemName: "cloud.sun.fill")
        Text("Weather Impact")
            .font(.headline)
        Spacer()
        weatherImpactBadge() // Color-coded badge
    }

    // Key Metrics (2x2 Grid)
    LazyVGrid(columns: [GridItem(), GridItem()]) {
        MetricCard(
            icon: "thermometer",
            value: "\(analysis.average_temperature_celsius)°C",
            label: "Avg Temp"
        )
        MetricCard(
            icon: "humidity",
            value: "\(analysis.average_humidity_percent)%",
            label: "Avg Humidity"
        )
        MetricCard(
            icon: "flame",
            value: "\(analysis.heat_stress_runs)",
            label: "Heat Stress Runs"
        )
        MetricCard(
            icon: "checkmark.circle",
            value: "\(analysis.ideal_condition_runs)",
            label: "Ideal Conditions"
        )
    }
}
```

#### **Weather Impact Badge Colors**
```swift
func weatherImpactBadge() -> some View {
    let (color, icon) = {
        switch analysis.weather_impact_score {
        case "minimal":   return (Color.green, "checkmark.circle.fill")
        case "moderate":  return (Color.orange, "exclamationmark.triangle.fill")
        case "significant": return (Color.red, "flame.fill")
        case "severe":    return (Color.purple, "exclamationmark.octagon.fill")
        default:          return (Color.gray, "questionmark.circle")
        }
    }()

    return Label(analysis.weather_impact_score.capitalized, systemImage: icon)
        .font(.caption.bold())
        .foregroundColor(color)
}
```

#### **Pace Impact Callout**
```swift
HStack {
    Image(systemName: "speedometer")
        .foregroundColor(.orange)
    Text("~\(Int(analysis.pace_degradation_seconds_per_mile))s/mile slower in heat")
        .font(.subheadline)
        .foregroundColor(.secondary)
}
.padding()
.background(Color.orange.opacity(0.1))
.cornerRadius(8)
```

#### **Heat Acclimation Indicator**
```swift
HStack {
    Text("Heat Acclimation:")
        .font(.subheadline)
        .foregroundColor(.secondary)

    Spacer()

    HStack(spacing: 4) {
        ForEach(0..<3) { index in
            Circle()
                .fill(acclimationLevel(index) ? Color.red : Color.gray.opacity(0.3))
                .frame(width: 8, height: 8)
        }
        Text(analysis.heat_acclimation_level.capitalized)
            .font(.caption.bold())
    }
}

func acclimationLevel(_ index: Int) -> Bool {
    switch analysis.heat_acclimation_level {
    case "well-acclimated": return true
    case "developing": return index < 2
    case "none": return index < 1
    default: return false
    }
}
```

#### **Optimal Training Times**
```swift
VStack(alignment: .leading, spacing: 8) {
    Label("Best Times to Train", systemImage: "clock.fill")
        .font(.subheadline.bold())

    ForEach(analysis.optimal_training_times, id: \.self) { time in
        HStack {
            Image(systemName: "sunrise.fill")
                .foregroundColor(.yellow)
            Text(time)
                .font(.body)
        }
        .padding(.vertical, 4)
    }
}
.padding()
.background(Color.blue.opacity(0.1))
.cornerRadius(12)
```

#### **Recommendations List**
```swift
VStack(alignment: .leading, spacing: 12) {
    Text("Recommendations")
        .font(.headline)

    ForEach(analysis.recommendations.prefix(3), id: \.self) { recommendation in
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: "lightbulb.fill")
                .foregroundColor(.yellow)
                .font(.caption)

            Text(recommendation)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.vertical, 4)
    }
}
```

---

## 2. VO2 Max & Race Predictions

### API Endpoint
```
GET /quick-wins/vo2max-estimate?limit=50
```

### Response Structure
```json
{
  "success": true,
  "estimate": {
    "vo2_max": 52.3,
    "fitness_level": "good",
    "estimation_method": "race_performance",
    "vvo2_max_pace": "4:15",
    "race_predictions": [
      {
        "distance": "5K",
        "distance_km": 5.0,
        "predicted_time": "0:21:45",
        "predicted_time_seconds": 1305,
        "pace_per_km": "4:21",
        "pace_per_mile": "6:59",
        "confidence": "high"
      },
      {
        "distance": "10K",
        "distance_km": 10.0,
        "predicted_time": "0:45:30",
        "predicted_time_seconds": 2730,
        "pace_per_km": "4:33",
        "pace_per_mile": "7:20",
        "confidence": "high"
      },
      {
        "distance": "Half Marathon",
        "distance_km": 21.0975,
        "predicted_time": "1:42:15",
        "predicted_time_seconds": 6135,
        "pace_per_km": "4:51",
        "pace_per_mile": "7:48",
        "confidence": "medium"
      },
      {
        "distance": "Marathon",
        "distance_km": 42.195,
        "predicted_time": "3:35:45",
        "predicted_time_seconds": 12945,
        "pace_per_km": "5:06",
        "pace_per_mile": "8:13",
        "confidence": "medium"
      }
    ],
    "recommendations": [
      "Your estimated VO2 max of 52.3 ml/kg/min places you in the 'good' category...",
      "Improve VO2 max with interval sessions..."
    ],
    "data_quality_score": 0.85
  }
}
```

### iOS View Components

#### **Hero Card - VO2 Max Display**
```swift
VStack(spacing: 16) {
    // Large VO2 Max Number
    VStack(spacing: 4) {
        Text("\(Int(estimate.vo2_max))")
            .font(.system(size: 60, weight: .bold, design: .rounded))
            .foregroundColor(fitnessLevelColor())

        Text("ml/kg/min")
            .font(.caption)
            .foregroundColor(.secondary)

        // Fitness Level Badge
        Text(estimate.fitness_level.uppercased())
            .font(.caption.bold())
            .padding(.horizontal, 12)
            .padding(.vertical, 4)
            .background(fitnessLevelColor().opacity(0.2))
            .foregroundColor(fitnessLevelColor())
            .cornerRadius(12)
    }

    // Fitness Level Bar
    fitnessLevelBar()
}
.padding()
.background(
    LinearGradient(
        colors: [fitnessLevelColor().opacity(0.1), Color.clear],
        startPoint: .top,
        endPoint: .bottom
    )
)
.cornerRadius(16)

func fitnessLevelColor() -> Color {
    switch estimate.fitness_level {
    case "elite": return .purple
    case "excellent": return .blue
    case "good": return .green
    case "average": return .orange
    default: return .gray
    }
}
```

#### **Fitness Level Progress Bar**
```swift
func fitnessLevelBar() -> some View {
    VStack(alignment: .leading, spacing: 8) {
        HStack {
            Text("Fitness Level")
                .font(.caption)
                .foregroundColor(.secondary)
            Spacer()
            Text("Data Quality: \(Int(estimate.data_quality_score * 100))%")
                .font(.caption)
                .foregroundColor(.secondary)
        }

        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                // Background
                Rectangle()
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 8)
                    .cornerRadius(4)

                // Progress
                Rectangle()
                    .fill(
                        LinearGradient(
                            colors: [.orange, .green, .blue, .purple],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: geometry.size.width * progressPercentage(), height: 8)
                    .cornerRadius(4)
            }
        }
        .frame(height: 8)

        // Labels
        HStack {
            Text("Below Avg")
                .font(.caption2)
            Spacer()
            Text("Average")
                .font(.caption2)
            Spacer()
            Text("Good")
                .font(.caption2)
            Spacer()
            Text("Excellent")
                .font(.caption2)
            Spacer()
            Text("Elite")
                .font(.caption2)
        }
        .foregroundColor(.secondary)
    }

    func progressPercentage() -> CGFloat {
        // Map VO2 max (25-85) to percentage (0-1)
        let normalized = (estimate.vo2_max - 25) / (85 - 25)
        return CGFloat(max(0, min(1, normalized)))
    }
}
```

#### **Race Predictions Card**
```swift
VStack(alignment: .leading, spacing: 16) {
    HStack {
        Image(systemName: "flag.checkered")
        Text("Race Time Predictions")
            .font(.headline)
        Spacer()
        Image(systemName: "info.circle")
            .foregroundColor(.secondary)
    }

    ForEach(estimate.race_predictions, id: \.distance) { prediction in
        RacePredictionRow(prediction: prediction)
    }
}
.padding()
.background(Color(.systemBackground))
.cornerRadius(16)
.shadow(radius: 2)

struct RacePredictionRow: View {
    let prediction: RacePrediction

    var body: some View {
        VStack(spacing: 8) {
            HStack {
                // Distance
                VStack(alignment: .leading) {
                    Text(prediction.distance)
                        .font(.headline)
                    Text("\(String(format: "%.2f", prediction.distance_km)) km")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                // Predicted Time
                VStack(alignment: .trailing) {
                    Text(prediction.predicted_time)
                        .font(.title3.bold())
                        .foregroundColor(.primary)

                    Text(prediction.pace_per_mile + "/mi")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            // Confidence Indicator
            HStack {
                ProgressView(value: confidenceValue())
                    .tint(confidenceColor())

                Text(prediction.confidence.capitalized)
                    .font(.caption.bold())
                    .foregroundColor(confidenceColor())
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }

    func confidenceValue() -> Double {
        switch prediction.confidence {
        case "high": return 0.9
        case "medium": return 0.6
        case "low": return 0.3
        default: return 0.5
        }
    }

    func confidenceColor() -> Color {
        switch prediction.confidence {
        case "high": return .green
        case "medium": return .orange
        case "low": return .red
        default: return .gray
        }
    }
}
```

#### **vVO2 Max Training Target**
```swift
if let vvo2Pace = estimate.vvo2_max_pace {
    HStack {
        VStack(alignment: .leading, spacing: 4) {
            Text("Interval Training Target")
                .font(.subheadline.bold())
            Text("Run intervals at this pace for 4-8 minutes")
                .font(.caption)
                .foregroundColor(.secondary)
        }

        Spacer()

        VStack(alignment: .trailing) {
            Text(vvo2Pace)
                .font(.title2.bold())
                .foregroundColor(.red)
            Text("per km")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
    .padding()
    .background(Color.red.opacity(0.1))
    .cornerRadius(12)
}
```

---

## 3. Training Load & Recovery

### API Endpoint
```
GET /quick-wins/training-load?limit=60
```

### Response Structure
```json
{
  "success": true,
  "analysis": {
    "acute_load_7_days": 285.3,
    "chronic_load_28_days": 312.8,
    "acwr": 0.91,
    "weekly_tss": 285.3,
    "total_volume_km": 45.2,
    "recovery_status": "adequate",
    "injury_risk_level": "low",
    "training_trend": "steady",
    "fitness_trend": "improving",
    "recommendations": [
      "✓ ACWR is 0.91 (optimal zone)...",
      "Recovery essentials: 7-9 hours sleep..."
    ],
    "daily_recommendations": {
      "Day 1": "40min easy run",
      "Day 2": "45min moderate run with 5x2min pickups",
      "Day 3": "30min recovery run",
      "Day 4": "50min tempo run (15min at threshold)",
      "Day 5": "Rest",
      "Day 6": "40min easy run",
      "Day 7": "75min long run (easy pace)"
    }
  }
}
```

### iOS View Components

#### **ACWR Gauge (Primary Metric)**
```swift
ZStack {
    // Background Circle
    Circle()
        .stroke(Color.gray.opacity(0.2), lineWidth: 20)
        .frame(width: 200, height: 200)

    // ACWR Arc
    Circle()
        .trim(from: 0, to: acwrProgress())
        .stroke(
            acwrColor(),
            style: StrokeStyle(lineWidth: 20, lineCap: .round)
        )
        .frame(width: 200, height: 200)
        .rotationEffect(.degrees(-90))
        .animation(.easeInOut, value: analysis.acwr)

    // Center Content
    VStack(spacing: 4) {
        Text(String(format: "%.2f", analysis.acwr))
            .font(.system(size: 48, weight: .bold, design: .rounded))
            .foregroundColor(acwrColor())

        Text("ACWR")
            .font(.caption)
            .foregroundColor(.secondary)

        Text(injuryRiskText())
            .font(.caption.bold())
            .foregroundColor(acwrColor())
    }
}

func acwrProgress() -> CGFloat {
    // Map ACWR (0-2.0) to progress (0-1)
    return CGFloat(min(analysis.acwr / 2.0, 1.0))
}

func acwrColor() -> Color {
    switch analysis.injury_risk_level {
    case "low": return .green
    case "moderate": return .orange
    case "high": return .red
    case "very_high": return .purple
    default: return .gray
    }
}

func injuryRiskText() -> String {
    analysis.injury_risk_level.uppercased() + " RISK"
}
```

#### **ACWR Zone Indicator**
```swift
VStack(alignment: .leading, spacing: 12) {
    Text("Optimal Zone: 0.8 - 1.3")
        .font(.caption.bold())
        .foregroundColor(.secondary)

    GeometryReader { geometry in
        ZStack(alignment: .leading) {
            // Zones
            HStack(spacing: 0) {
                Rectangle()
                    .fill(Color.blue.opacity(0.3))
                    .frame(width: geometry.size.width * 0.4) // 0-0.8

                Rectangle()
                    .fill(Color.green.opacity(0.3))
                    .frame(width: geometry.size.width * 0.25) // 0.8-1.3

                Rectangle()
                    .fill(Color.orange.opacity(0.3))
                    .frame(width: geometry.size.width * 0.1) // 1.3-1.5

                Rectangle()
                    .fill(Color.red.opacity(0.3))
                    .frame(width: geometry.size.width * 0.25) // 1.5+
            }

            // Current Position Marker
            Circle()
                .fill(acwrColor())
                .frame(width: 16, height: 16)
                .offset(x: geometry.size.width * CGFloat(min(analysis.acwr / 2.0, 1.0)) - 8)
        }
    }
    .frame(height: 30)
    .cornerRadius(15)

    HStack {
        Text("Detraining")
            .font(.caption2)
        Spacer()
        Text("Optimal")
            .font(.caption2.bold())
        Spacer()
        Text("High Risk")
            .font(.caption2)
    }
    .foregroundColor(.secondary)
}
```

#### **Training Load Stats Grid**
```swift
LazyVGrid(columns: [GridItem(), GridItem()], spacing: 16) {
    StatCard(
        icon: "bolt.fill",
        value: "\(Int(analysis.acute_load_7_days))",
        label: "Acute Load (7d)",
        color: .orange
    )

    StatCard(
        icon: "chart.line.uptrend.xyaxis",
        value: "\(Int(analysis.chronic_load_28_days))",
        label: "Chronic Load (28d)",
        color: .blue
    )

    StatCard(
        icon: "flame.fill",
        value: "\(Int(analysis.weekly_tss))",
        label: "Weekly TSS",
        color: .red
    )

    StatCard(
        icon: "figure.run",
        value: String(format: "%.1f km", analysis.total_volume_km),
        label: "Weekly Volume",
        color: .green
    )
}

struct StatCard: View {
    let icon: String
    let value: String
    let label: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)

            Text(value)
                .font(.title3.bold())

            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}
```

#### **Recovery Status Banner**
```swift
HStack(spacing: 12) {
    Image(systemName: recoveryIcon())
        .font(.title2)
        .foregroundColor(recoveryColor())

    VStack(alignment: .leading, spacing: 4) {
        Text("Recovery Status")
            .font(.caption)
            .foregroundColor(.secondary)

        Text(analysis.recovery_status.replacingOccurrences(of: "_", with: " ").capitalized)
            .font(.headline)
            .foregroundColor(recoveryColor())
    }

    Spacer()

    Image(systemName: "chevron.right")
        .foregroundColor(.secondary)
}
.padding()
.background(recoveryColor().opacity(0.1))
.cornerRadius(12)

func recoveryIcon() -> String {
    switch analysis.recovery_status {
    case "well_recovered": return "checkmark.circle.fill"
    case "adequate": return "checkmark.circle"
    case "fatigued": return "exclamationmark.triangle.fill"
    case "overreaching": return "exclamationmark.octagon.fill"
    case "overtrained": return "xmark.octagon.fill"
    default: return "circle"
    }
}

func recoveryColor() -> Color {
    switch analysis.recovery_status {
    case "well_recovered": return .green
    case "adequate": return .blue
    case "fatigued": return .orange
    case "overreaching": return .red
    case "overtrained": return .purple
    default: return .gray
    }
}
```

#### **Training Trend Indicator**
```swift
HStack {
    VStack(alignment: .leading, spacing: 4) {
        Text("Training Trend")
            .font(.caption)
            .foregroundColor(.secondary)

        HStack {
            Image(systemName: trendIcon())
                .foregroundColor(trendColor())

            Text(analysis.training_trend.replacingOccurrences(of: "_", with: " ").capitalized)
                .font(.subheadline.bold())
        }
    }

    Spacer()

    VStack(alignment: .trailing, spacing: 4) {
        Text("Fitness Trend")
            .font(.caption)
            .foregroundColor(.secondary)

        HStack {
            Text(analysis.fitness_trend.capitalized)
                .font(.subheadline.bold())
                .foregroundColor(fitnessColor())

            Image(systemName: fitnessIcon())
                .foregroundColor(fitnessColor())
        }
    }
}
.padding()
.background(Color.gray.opacity(0.05))
.cornerRadius(12)

func trendIcon() -> String {
    switch analysis.training_trend {
    case "ramping_up": return "arrow.up.circle.fill"
    case "steady": return "equal.circle.fill"
    case "tapering": return "arrow.down.circle.fill"
    case "detraining": return "arrow.down.circle"
    default: return "circle"
    }
}

func trendColor() -> Color {
    switch analysis.training_trend {
    case "ramping_up": return .orange
    case "steady": return .blue
    case "tapering": return .green
    case "detraining": return .gray
    default: return .gray
    }
}

func fitnessIcon() -> String {
    switch analysis.fitness_trend {
    case "improving": return "arrow.up.right.circle.fill"
    case "maintaining": return "arrow.right.circle.fill"
    case "declining": return "arrow.down.right.circle.fill"
    default: return "circle"
    }
}

func fitnessColor() -> Color {
    switch analysis.fitness_trend {
    case "improving": return .green
    case "maintaining": return .blue
    case "declining": return .red
    default: return .gray
    }
}
```

#### **7-Day Workout Plan**
```swift
VStack(alignment: .leading, spacing: 12) {
    Text("Next 7 Days")
        .font(.headline)

    ForEach(Array(analysis.daily_recommendations.sorted(by: { $0.key < $1.key })), id: \.key) { day, workout in
        HStack(alignment: .top, spacing: 12) {
            // Day Badge
            Text(day)
                .font(.caption.bold())
                .foregroundColor(.white)
                .frame(width: 60)
                .padding(.vertical, 6)
                .background(dayColor(workout: workout))
                .cornerRadius(8)

            // Workout
            VStack(alignment: .leading, spacing: 4) {
                Text(workout)
                    .font(.subheadline)
                    .foregroundColor(.primary)

                if workout.lowercased().contains("rest") {
                    Label("Recovery", systemImage: "heart.fill")
                        .font(.caption)
                        .foregroundColor(.green)
                } else if workout.lowercased().contains("tempo") || workout.lowercased().contains("interval") {
                    Label("High Intensity", systemImage: "bolt.fill")
                        .font(.caption)
                        .foregroundColor(.red)
                } else {
                    Label("Base Building", systemImage: "figure.run")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }

            Spacer()
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }
}

func dayColor(workout: String) -> Color {
    if workout.lowercased().contains("rest") {
        return .green
    } else if workout.lowercased().contains("tempo") || workout.lowercased().contains("interval") {
        return .red
    } else if workout.lowercased().contains("long") {
        return .purple
    } else {
        return .blue
    }
}
```

---

## 4. Comprehensive Dashboard View

### API Endpoint
```
GET /quick-wins/comprehensive-analysis
```

### Response Structure
```json
{
  "success": true,
  "user_id": "123",
  "analysis_date": "2025-10-01T17:30:00Z",
  "analyses": {
    "weather_context": { /* ... */ },
    "vo2max_estimate": { /* ... */ },
    "training_load": { /* ... */ }
  },
  "priority_recommendations": [
    "✓ ACWR is 0.91 (optimal zone)...",
    "Your estimated VO2 max of 52.3...",
    "Average training temperature (24.5°C)...",
    "Recovery essentials: 7-9 hours sleep...",
    "Continue VO2 max intervals weekly..."
  ]
}
```

### iOS View Components

#### **Quick Stats Overview (Top of Dashboard)**
```swift
ScrollView(.horizontal, showsIndicators: false) {
    HStack(spacing: 16) {
        QuickStatCard(
            icon: "bolt.fill",
            value: String(format: "%.2f", trainingLoad.acwr),
            label: "ACWR",
            color: acwrColor(),
            trend: .neutral
        )

        QuickStatCard(
            icon: "lungs.fill",
            value: "\(Int(vo2max.vo2_max))",
            label: "VO2 Max",
            color: fitnessLevelColor(),
            trend: .up
        )

        QuickStatCard(
            icon: "thermometer",
            value: "\(Int(weather.average_temperature_celsius))°C",
            label: "Avg Temp",
            color: tempColor(),
            trend: .neutral
        )

        QuickStatCard(
            icon: "figure.run",
            value: String(format: "%.1f", trainingLoad.total_volume_km),
            label: "Weekly km",
            color: .green,
            trend: .up
        )
    }
    .padding(.horizontal)
}

struct QuickStatCard: View {
    let icon: String
    let value: String
    let label: String
    let color: Color
    let trend: Trend

    enum Trend {
        case up, down, neutral
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Spacer()
                if trend != .neutral {
                    Image(systemName: trend == .up ? "arrow.up.right" : "arrow.down.right")
                        .font(.caption)
                        .foregroundColor(trend == .up ? .green : .red)
                }
            }

            Text(value)
                .font(.title2.bold())

            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(width: 120)
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}
```

#### **Priority Recommendations Banner**
```swift
VStack(alignment: .leading, spacing: 12) {
    HStack {
        Image(systemName: "exclamationmark.triangle.fill")
            .foregroundColor(.orange)
        Text("Top Recommendations")
            .font(.headline)
        Spacer()
        Button(action: { /* Show all */ }) {
            Text("See All")
                .font(.caption)
        }
    }

    ForEach(analysis.priority_recommendations.prefix(3), id: \.self) { recommendation in
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: recommendationIcon(recommendation))
                .foregroundColor(recommendationColor(recommendation))
                .font(.caption)

            Text(recommendation)
                .font(.subheadline)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(.vertical, 4)
    }
}
.padding()
.background(
    LinearGradient(
        colors: [Color.orange.opacity(0.1), Color.clear],
        startPoint: .top,
        endPoint: .bottom
    )
)
.cornerRadius(12)

func recommendationIcon(_ text: String) -> String {
    if text.contains("✓") || text.contains("optimal") {
        return "checkmark.circle.fill"
    } else if text.contains("⚠️") || text.contains("WARNING") {
        return "exclamationmark.triangle.fill"
    } else {
        return "lightbulb.fill"
    }
}

func recommendationColor(_ text: String) -> Color {
    if text.contains("✓") || text.contains("optimal") {
        return .green
    } else if text.contains("⚠️") || text.contains("WARNING") {
        return .red
    } else {
        return .blue
    }
}
```

#### **Section Navigation Cards**
```swift
LazyVGrid(columns: [GridItem(), GridItem()], spacing: 16) {
    NavigationCard(
        icon: "cloud.sun.fill",
        title: "Weather Impact",
        subtitle: weather.weather_impact_score.capitalized,
        color: .orange,
        destination: WeatherDetailView()
    )

    NavigationCard(
        icon: "lungs.fill",
        title: "Race Predictions",
        subtitle: "\(vo2max.race_predictions.count) races",
        color: .blue,
        destination: RacePredictionsView()
    )

    NavigationCard(
        icon: "bolt.fill",
        title: "Training Load",
        subtitle: trainingLoad.recovery_status.capitalized,
        color: .green,
        destination: TrainingLoadView()
    )

    NavigationCard(
        icon: "calendar",
        title: "7-Day Plan",
        subtitle: "Personalized",
        color: .purple,
        destination: WorkoutPlanView()
    )
}

struct NavigationCard<Destination: View>: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    let destination: Destination

    var body: some View {
        NavigationLink(destination: destination) {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Image(systemName: icon)
                        .font(.title2)
                        .foregroundColor(color)
                    Spacer()
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(color.opacity(0.1))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}
```

---

## 5. Recommended View Hierarchy

```
TabView
├── Dashboard (Comprehensive Overview)
│   ├── Quick Stats Carousel
│   ├── Priority Recommendations
│   └── Section Navigation Grid
│
├── Weather Impact
│   ├── Hero Card (Summary)
│   ├── Pace Impact Callout
│   ├── Heat Acclimation Indicator
│   ├── Optimal Training Times
│   └── Detailed Recommendations
│
├── Fitness & Racing
│   ├── VO2 Max Gauge
│   ├── Fitness Level Bar
│   ├── Race Predictions List
│   ├── vVO2 Max Training Target
│   └── Training Recommendations
│
└── Training Load
    ├── ACWR Gauge
    ├── Zone Indicator
    ├── Load Stats Grid
    ├── Recovery Status
    ├── Training Trends
    └── 7-Day Workout Plan
```

---

## 6. SwiftUI Models

```swift
// MARK: - API Response Models

struct QuickWinsResponse: Codable {
    let success: Bool
    let analyses: QuickWinsAnalyses
    let priority_recommendations: [String]
}

struct QuickWinsAnalyses: Codable {
    let weather_context: WeatherAnalysis
    let vo2max_estimate: VO2MaxEstimate
    let training_load: TrainingLoadAnalysis
}

// MARK: - Weather Models

struct WeatherAnalysis: Codable {
    let average_temperature_celsius: Double
    let average_humidity_percent: Double
    let heat_stress_runs: Int
    let ideal_condition_runs: Int
    let weather_impact_score: String
    let pace_degradation_seconds_per_mile: Double
    let heat_acclimation_level: String
    let optimal_training_times: [String]
    let recommendations: [String]
}

// MARK: - VO2 Max Models

struct VO2MaxEstimate: Codable {
    let vo2_max: Double
    let fitness_level: String
    let estimation_method: String
    let vvo2_max_pace: String?
    let race_predictions: [RacePrediction]
    let recommendations: [String]
    let data_quality_score: Double
}

struct RacePrediction: Codable, Identifiable {
    var id: String { distance }

    let distance: String
    let distance_km: Double
    let predicted_time: String
    let predicted_time_seconds: Int
    let pace_per_km: String
    let pace_per_mile: String
    let confidence: String
}

// MARK: - Training Load Models

struct TrainingLoadAnalysis: Codable {
    let acute_load_7_days: Double
    let chronic_load_28_days: Double
    let acwr: Double
    let weekly_tss: Double
    let total_volume_km: Double
    let recovery_status: String
    let injury_risk_level: String
    let training_trend: String
    let fitness_trend: String
    let recommendations: [String]
    let daily_recommendations: [String: String]
}
```

---

## 7. API Service Layer

```swift
class QuickWinsService: ObservableObject {
    @Published var isLoading = false
    @Published var error: Error?

    private let baseURL = "https://your-api.com"
    private let token: String

    init(token: String) {
        self.token = token
    }

    func fetchComprehensiveAnalysis() async throws -> QuickWinsResponse {
        isLoading = true
        defer { isLoading = false }

        let url = URL(string: "\(baseURL)/quick-wins/comprehensive-analysis")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw QuickWinsError.invalidResponse
        }

        return try JSONDecoder().decode(QuickWinsResponse.self, from: data)
    }

    func fetchWeatherImpact(limit: Int = 30) async throws -> WeatherAnalysis {
        // Similar implementation
    }

    func fetchVO2MaxEstimate(limit: Int = 50) async throws -> VO2MaxEstimate {
        // Similar implementation
    }

    func fetchTrainingLoad(limit: Int = 60) async throws -> TrainingLoadAnalysis {
        // Similar implementation
    }
}

enum QuickWinsError: Error {
    case invalidResponse
    case decodingError
    case networkError
}
```

---

## 8. Refresh & Caching Strategy

```swift
class QuickWinsViewModel: ObservableObject {
    @Published var data: QuickWinsResponse?
    @Published var isLoading = false
    @Published var lastUpdated: Date?

    private let service: QuickWinsService
    private let cacheKey = "quick_wins_cache"
    private let cacheExpiration: TimeInterval = 3600 // 1 hour

    init(service: QuickWinsService) {
        self.service = service
        loadFromCache()
    }

    func refresh() async {
        guard !isLoading else { return }

        isLoading = true

        do {
            let response = try await service.fetchComprehensiveAnalysis()

            await MainActor.run {
                self.data = response
                self.lastUpdated = Date()
                self.isLoading = false
                self.saveToCache(response)
            }
        } catch {
            await MainActor.run {
                self.isLoading = false
                print("Error fetching data: \(error)")
            }
        }
    }

    private func loadFromCache() {
        // Load from UserDefaults or Core Data
    }

    private func saveToCache(_ data: QuickWinsResponse) {
        // Save to UserDefaults or Core Data
    }

    func shouldRefresh() -> Bool {
        guard let lastUpdated = lastUpdated else { return true }
        return Date().timeIntervalSince(lastUpdated) > cacheExpiration
    }
}
```

---

## 9. Pull-to-Refresh Implementation

```swift
struct QuickWinsDashboard: View {
    @StateObject private var viewModel: QuickWinsViewModel

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                if let data = viewModel.data {
                    QuickStatsCarousel(data: data)
                    PriorityRecommendations(recommendations: data.priority_recommendations)
                    SectionNavigationGrid(data: data)
                } else {
                    ProgressView("Loading insights...")
                }
            }
            .padding()
        }
        .refreshable {
            await viewModel.refresh()
        }
        .navigationTitle("Quick Wins")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                if let lastUpdated = viewModel.lastUpdated {
                    Text(lastUpdated, style: .relative)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .task {
            if viewModel.shouldRefresh() {
                await viewModel.refresh()
            }
        }
    }
}
```

---

## 10. Color Palette Recommendations

```swift
extension Color {
    // Weather
    static let weatherMinimal = Color.green
    static let weatherModerate = Color.orange
    static let weatherSignificant = Color.red
    static let weatherSevere = Color.purple

    // Fitness Levels
    static let fitnessElite = Color.purple
    static let fitnessExcellent = Color.blue
    static let fitnessGood = Color.green
    static let fitnessAverage = Color.orange
    static let fitnessBelowAverage = Color.gray

    // ACWR / Injury Risk
    static let riskLow = Color.green
    static let riskModerate = Color.orange
    static let riskHigh = Color.red
    static let riskVeryHigh = Color.purple

    // Recovery Status
    static let recoveryWell = Color.green
    static let recoveryAdequate = Color.blue
    static let recoveryFatigued = Color.orange
    static let recoveryOverreaching = Color.red
    static let recoveryOvertrained = Color.purple
}
```

---

## Summary

This specification provides everything needed to build comprehensive iOS views for all Quick Wins features:

✅ **4 Main Views**: Weather, VO2 Max/Racing, Training Load, Dashboard
✅ **Complete API integration**: All endpoints with response structures
✅ **SwiftUI components**: Copy-paste ready code snippets
✅ **Data models**: Codable structs for all responses
✅ **Service layer**: API client with authentication
✅ **Caching strategy**: Performance optimization
✅ **Color system**: Consistent design language

**Estimated Development Time**: 2-3 days for full implementation
