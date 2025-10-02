# iOS Development Prompt: Quick Wins Features

Hi Claude! I need your help implementing three new AI-powered features in my iOS running coach app. These features integrate with our backend API that provides weather impact analysis, VO2 max estimation with race predictions, and training load monitoring with injury risk assessment.

---

## Project Context

**App**: Running coach iOS app (SwiftUI)
**Backend API**: FastAPI server with AI agents
**Authentication**: JWT tokens via Bearer authorization
**Base URL**: `https://runaway-coach-api-203308554831.us-central1.run.app` (replace with actual)

---

## Task Overview

Implement **4 new screens** that display insights from our AI coaching agents:

1. **Dashboard** - Comprehensive overview with quick stats and navigation
2. **Weather Impact** - Weather analysis affecting running performance
3. **VO2 Max & Racing** - Fitness estimation and race time predictions
4. **Training Load** - ACWR-based injury risk and recovery monitoring

---

## API Endpoints

### 1. Comprehensive Analysis (Use this for Dashboard)
```
GET /quick-wins/comprehensive-analysis
Authorization: Bearer {JWT_TOKEN}

Response:
{
  "success": true,
  "user_id": "123",
  "analysis_date": "2025-10-01T17:30:00Z",
  "analyses": {
    "weather_context": {
      "average_temperature_celsius": 24.5,
      "average_humidity_percent": 68.2,
      "heat_stress_runs": 12,
      "ideal_condition_runs": 8,
      "weather_impact_score": "moderate",
      "pace_degradation_seconds_per_mile": 15.2,
      "heat_acclimation_level": "developing",
      "optimal_training_times": ["5:00-7:00 AM", "8:00-10:00 PM"],
      "recommendations": ["...", "..."]
    },
    "vo2max_estimate": {
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
        }
        // ... 10K, Half Marathon, Marathon
      ],
      "recommendations": ["...", "..."],
      "data_quality_score": 0.85
    },
    "training_load": {
      "acute_load_7_days": 285.3,
      "chronic_load_28_days": 312.8,
      "acwr": 0.91,
      "weekly_tss": 285.3,
      "total_volume_km": 45.2,
      "recovery_status": "adequate",
      "injury_risk_level": "low",
      "training_trend": "steady",
      "fitness_trend": "improving",
      "recommendations": ["...", "..."],
      "daily_recommendations": {
        "Day 1": "40min easy run",
        "Day 2": "45min moderate run with 5x2min pickups",
        // ... Day 3-7
      }
    }
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

### 2. Individual Endpoints (for detail views)
```
GET /quick-wins/weather-impact?limit=30
GET /quick-wins/vo2max-estimate?limit=50
GET /quick-wins/training-load?limit=60
```

---

## Data Models to Create

```swift
// MARK: - Main Response Model
struct QuickWinsResponse: Codable {
    let success: Bool
    let userId: String
    let analysisDate: String
    let analyses: QuickWinsAnalyses
    let priorityRecommendations: [String]

    enum CodingKeys: String, CodingKey {
        case success
        case userId = "user_id"
        case analysisDate = "analysis_date"
        case analyses
        case priorityRecommendations = "priority_recommendations"
    }
}

struct QuickWinsAnalyses: Codable {
    let weatherContext: WeatherAnalysis
    let vo2maxEstimate: VO2MaxEstimate
    let trainingLoad: TrainingLoadAnalysis

    enum CodingKeys: String, CodingKey {
        case weatherContext = "weather_context"
        case vo2maxEstimate = "vo2max_estimate"
        case trainingLoad = "training_load"
    }
}

// MARK: - Weather Models
struct WeatherAnalysis: Codable {
    let averageTemperatureCelsius: Double
    let averageHumidityPercent: Double
    let heatStressRuns: Int
    let idealConditionRuns: Int
    let weatherImpactScore: String // "minimal", "moderate", "significant", "severe"
    let paceDegradationSecondsPerMile: Double
    let heatAcclimationLevel: String // "none", "developing", "well-acclimated"
    let optimalTrainingTimes: [String]
    let recommendations: [String]

    enum CodingKeys: String, CodingKey {
        case averageTemperatureCelsius = "average_temperature_celsius"
        case averageHumidityPercent = "average_humidity_percent"
        case heatStressRuns = "heat_stress_runs"
        case idealConditionRuns = "ideal_condition_runs"
        case weatherImpactScore = "weather_impact_score"
        case paceDegradationSecondsPerMile = "pace_degradation_seconds_per_mile"
        case heatAcclimationLevel = "heat_acclimation_level"
        case optimalTrainingTimes = "optimal_training_times"
        case recommendations
    }
}

// MARK: - VO2 Max Models
struct VO2MaxEstimate: Codable {
    let vo2Max: Double
    let fitnessLevel: String // "elite", "excellent", "good", "average", "below_average"
    let estimationMethod: String
    let vvo2MaxPace: String?
    let racePredictions: [RacePrediction]
    let recommendations: [String]
    let dataQualityScore: Double

    enum CodingKeys: String, CodingKey {
        case vo2Max = "vo2_max"
        case fitnessLevel = "fitness_level"
        case estimationMethod = "estimation_method"
        case vvo2MaxPace = "vvo2_max_pace"
        case racePredictions = "race_predictions"
        case recommendations
        case dataQualityScore = "data_quality_score"
    }
}

struct RacePrediction: Codable, Identifiable {
    var id: String { distance }

    let distance: String
    let distanceKm: Double
    let predictedTime: String
    let predictedTimeSeconds: Int
    let pacePerKm: String
    let pacePerMile: String
    let confidence: String // "high", "medium", "low"

    enum CodingKeys: String, CodingKey {
        case distance
        case distanceKm = "distance_km"
        case predictedTime = "predicted_time"
        case predictedTimeSeconds = "predicted_time_seconds"
        case pacePerKm = "pace_per_km"
        case pacePerMile = "pace_per_mile"
        case confidence
    }
}

// MARK: - Training Load Models
struct TrainingLoadAnalysis: Codable {
    let acuteLoad7Days: Double
    let chronicLoad28Days: Double
    let acwr: Double
    let weeklyTss: Double
    let totalVolumeKm: Double
    let recoveryStatus: String // "well_recovered", "adequate", "fatigued", "overreaching", "overtrained"
    let injuryRiskLevel: String // "low", "moderate", "high", "very_high"
    let trainingTrend: String // "ramping_up", "steady", "tapering", "detraining"
    let fitnessTrend: String // "improving", "maintaining", "declining"
    let recommendations: [String]
    let dailyRecommendations: [String: String]

    enum CodingKeys: String, CodingKey {
        case acuteLoad7Days = "acute_load_7_days"
        case chronicLoad28Days = "chronic_load_28_days"
        case acwr
        case weeklyTss = "weekly_tss"
        case totalVolumeKm = "total_volume_km"
        case recoveryStatus = "recovery_status"
        case injuryRiskLevel = "injury_risk_level"
        case trainingTrend = "training_trend"
        case fitnessTrend = "fitness_trend"
        case recommendations
        case dailyRecommendations = "daily_recommendations"
    }
}
```

---

## API Service to Create

```swift
class QuickWinsService: ObservableObject {
    private let baseURL = "https://your-api.com" // TODO: Replace with actual URL
    private let authToken: String

    @Published var isLoading = false
    @Published var error: String?

    init(authToken: String) {
        self.authToken = authToken
    }

    func fetchComprehensiveAnalysis() async throws -> QuickWinsResponse {
        isLoading = true
        defer { isLoading = false }

        let url = URL(string: "\(baseURL)/quick-wins/comprehensive-analysis")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw QuickWinsError.invalidResponse
        }

        let decoder = JSONDecoder()
        return try decoder.decode(QuickWinsResponse.self, from: data)
    }
}

enum QuickWinsError: Error {
    case invalidResponse
    case decodingError
    case networkError
}
```

---

## UI Requirements

### Screen 1: Dashboard (Main Quick Wins Overview)

**Layout:**
```
NavigationView {
    ScrollView {
        VStack(spacing: 20) {
            // 1. Quick Stats Carousel (horizontal scroll)
            // 2. Priority Recommendations Banner
            // 3. Section Navigation Cards (2x2 grid)
        }
    }
    .refreshable { await refresh() }
    .navigationTitle("Quick Wins")
}
```

**Components Needed:**

1. **Quick Stats Carousel** - Horizontal scrolling cards showing:
   - ACWR value with color-coded badge
   - VO2 Max value with fitness level
   - Average temperature
   - Weekly mileage

2. **Priority Recommendations Banner** - Top 3 recommendations with:
   - Warning/success icons
   - Truncated text (expandable)
   - "See All" button

3. **Navigation Grid** - 2x2 cards:
   - Weather Impact (orange theme)
   - Race Predictions (blue theme)
   - Training Load (green theme)
   - 7-Day Plan (purple theme)

**Color Logic for Quick Stats:**
- ACWR: Green (<0.8), Blue (0.8-1.3), Orange (1.3-1.5), Red (>1.5)
- VO2 Max: Based on fitness level (see below)
- Temperature: Blue (<15°C), Green (15-20°C), Orange (20-25°C), Red (>25°C)

---

### Screen 2: Weather Impact Detail

**Key UI Elements:**

1. **Hero Card** with:
   - Weather impact badge (color-coded: green/orange/red/purple)
   - 2x2 grid of metrics (temp, humidity, heat runs, ideal runs)

2. **Pace Impact Callout**:
   - Orange background
   - Speedometer icon
   - "~Xs/mile slower in heat" text

3. **Heat Acclimation Indicator**:
   - 3-level dots (filled based on level)
   - "none" = 1 dot, "developing" = 2 dots, "well-acclimated" = 3 dots

4. **Optimal Training Times List**:
   - Blue background cards
   - Sunrise/sunset icons
   - Time ranges

5. **Recommendations List**:
   - Lightbulb icons
   - Multi-line text support

**Color Coding for Weather Impact:**
```swift
func weatherImpactColor(_ score: String) -> Color {
    switch score {
    case "minimal": return .green
    case "moderate": return .orange
    case "significant": return .red
    case "severe": return .purple
    default: return .gray
    }
}
```

---

### Screen 3: VO2 Max & Race Predictions

**Key UI Elements:**

1. **VO2 Max Hero Card**:
   - Large centered number (60pt bold)
   - "ml/kg/min" subtitle
   - Fitness level badge below
   - Gradient background based on fitness level

2. **Fitness Level Progress Bar**:
   - Rainbow gradient (orange → green → blue → purple)
   - Labels: "Below Avg", "Average", "Good", "Excellent", "Elite"
   - Current position marker
   - Data quality percentage

3. **Race Predictions List** - For each race (5K, 10K, Half, Marathon):
   - Distance name and km
   - Predicted time (large, bold)
   - Pace per mile
   - Confidence indicator (progress bar: green/orange/red)

4. **vVO2 Max Training Card** (if available):
   - Red background
   - Pace value (large)
   - "Interval Training Target" label

**Fitness Level Colors:**
```swift
func fitnessLevelColor(_ level: String) -> Color {
    switch level {
    case "elite": return .purple
    case "excellent": return .blue
    case "good": return .green
    case "average": return .orange
    default: return .gray
    }
}
```

---

### Screen 4: Training Load & Recovery

**Key UI Elements:**

1. **ACWR Circular Gauge** (primary metric):
   - Large circular progress indicator
   - ACWR value in center (48pt bold)
   - Color-coded stroke based on injury risk
   - Risk level text below ("LOW RISK", etc.)

2. **ACWR Zone Indicator**:
   - Horizontal bar with 4 zones
   - Blue (0-0.8), Green (0.8-1.3), Orange (1.3-1.5), Red (1.5+)
   - Current position marker (circle)
   - Labels: "Detraining", "Optimal", "High Risk"

3. **Stats Grid (2x2)**:
   - Acute Load (7d) - orange background
   - Chronic Load (28d) - blue background
   - Weekly TSS - red background
   - Weekly Volume - green background

4. **Recovery Status Banner**:
   - Color-coded based on status
   - Icon (checkmark/warning/error)
   - Tap to see details

5. **Training Trends Row**:
   - Training Trend (left): arrow icon + text
   - Fitness Trend (right): arrow icon + text
   - Color-coded arrows

6. **7-Day Workout Plan**:
   - Day badges (colored by workout type)
   - Workout description
   - Type indicator (Recovery/High Intensity/Base Building)

**Color Logic:**

```swift
// ACWR / Injury Risk
func acwrColor(_ risk: String) -> Color {
    switch risk {
    case "low": return .green
    case "moderate": return .orange
    case "high": return .red
    case "very_high": return .purple
    default: return .gray
    }
}

// Recovery Status
func recoveryColor(_ status: String) -> Color {
    switch status {
    case "well_recovered": return .green
    case "adequate": return .blue
    case "fatigued": return .orange
    case "overreaching": return .red
    case "overtrained": return .purple
    default: return .gray
    }
}

// Day Badge Color (workout plan)
func workoutColor(_ workout: String) -> Color {
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

## Implementation Steps

### Phase 1: Setup (Do First)
1. Create all data models with proper `CodingKeys`
2. Create `QuickWinsService` with `fetchComprehensiveAnalysis()` method
3. Add error handling enum
4. Test API connection and decode response

### Phase 2: Dashboard Screen
1. Create `QuickWinsDashboardView`
2. Add `QuickWinsViewModel` with `@StateObject`
3. Implement Quick Stats Carousel
4. Add Priority Recommendations section
5. Create Navigation Cards grid
6. Add pull-to-refresh

### Phase 3: Detail Screens
1. Create `WeatherImpactView` with all components
2. Create `VO2MaxRacingView` with gauge and predictions
3. Create `TrainingLoadView` with ACWR gauge and plan
4. Wire up navigation from dashboard cards

### Phase 4: Polish
1. Add loading states (ProgressView)
2. Add empty states ("No data available")
3. Add error handling UI
4. Implement 1-hour cache (UserDefaults)
5. Add "Last updated" timestamp

---

## Key Design Patterns to Use

✅ **MVVM Architecture**: Use `@StateObject` for ViewModels
✅ **Async/Await**: All API calls should use modern concurrency
✅ **Error Handling**: Try/catch with user-friendly error messages
✅ **Loading States**: Show ProgressView during API calls
✅ **Pull-to-Refresh**: Use `.refreshable` modifier
✅ **SF Symbols**: Use built-in icons (cloud.sun, bolt.fill, etc.)
✅ **Semantic Colors**: Color.green, .orange, .red for consistency
✅ **Lazy Loading**: Use LazyVGrid for grids
✅ **Safe Unwrapping**: Handle optionals properly (vvo2MaxPace, etc.)

---

## Important Notes

⚠️ **ACWR Interpretation:**
- 0.8 - 1.3 = **Optimal** (green/blue)
- < 0.8 = **Detraining** (blue)
- 1.3 - 1.5 = **Moderate Risk** (orange)
- > 1.5 = **High Risk** (red)

⚠️ **Temperature Display:**
- API returns Celsius
- Consider adding Fahrenheit conversion for US users

⚠️ **Time Formatting:**
- Race predictions: "0:21:45" format (H:MM:SS)
- Pace: "6:59" format (M:SS per mile)

⚠️ **Empty States:**
- If `race_predictions` is empty, show "Complete more runs to get predictions"
- If recommendations is empty, show default encouragement

---

## Example Usage in App

```swift
// In your main ContentView or TabView
struct MainTabView: View {
    @StateObject private var authManager = AuthManager()

    var body: some View {
        TabView {
            // Existing tabs...

            QuickWinsDashboardView(
                authToken: authManager.token
            )
            .tabItem {
                Label("Insights", systemImage: "chart.bar.fill")
            }
        }
    }
}
```

---

## Success Criteria

✅ All 4 screens render correctly with real API data
✅ Pull-to-refresh works on dashboard
✅ All colors match the risk/status levels
✅ Navigation flows from dashboard to detail views
✅ Loading states show during API calls
✅ Error handling displays user-friendly messages
✅ Works on iPhone (all sizes) and iPad
✅ Dark mode support (use semantic colors)
✅ Accessibility labels for VoiceOver

---

## Testing Checklist

- [ ] Dashboard loads comprehensive analysis
- [ ] Quick stats display correct values
- [ ] Navigation cards lead to correct detail screens
- [ ] Weather impact colors match severity
- [ ] VO2 Max gauge shows correct fitness level
- [ ] All 4 race predictions display
- [ ] ACWR gauge color matches injury risk
- [ ] 7-day workout plan shows all days
- [ ] Pull-to-refresh updates data
- [ ] Loading spinner shows during API calls
- [ ] Error state displays when API fails
- [ ] Works in light and dark mode

---

## Questions to Ask Me

If anything is unclear:
1. What's the actual API base URL?
2. How do I get the JWT auth token in the app?
3. Should I add Fahrenheit temperature conversion?
4. Do you want local caching (UserDefaults/Core Data)?
5. Should I add share functionality for race predictions?
6. Any specific branding colors to use instead of semantic colors?

---

## Expected Output

Please create:
1. All data models in `Models/QuickWins/`
2. API service in `Services/QuickWinsService.swift`
3. View models in `ViewModels/QuickWins/`
4. All 4 views in `Views/QuickWins/`
5. Shared components in `Views/QuickWins/Components/`

Let me know when you're ready and I'll provide any additional context you need!

---

## Bonus: Sample Test Data (for development)

If the API isn't ready, use this mock response:

```swift
extension QuickWinsResponse {
    static var mock: QuickWinsResponse {
        QuickWinsResponse(
            success: true,
            userId: "123",
            analysisDate: "2025-10-01T17:30:00Z",
            analyses: QuickWinsAnalyses(
                weatherContext: WeatherAnalysis(
                    averageTemperatureCelsius: 24.5,
                    averageHumidityPercent: 68.2,
                    heatStressRuns: 12,
                    idealConditionRuns: 8,
                    weatherImpactScore: "moderate",
                    paceDegradationSecondsPerMile: 15.2,
                    heatAcclimationLevel: "developing",
                    optimalTrainingTimes: ["5:00-7:00 AM", "8:00-10:00 PM"],
                    recommendations: [
                        "Average training temperature (24.5°C) is above ideal. Expect 15s/mile slower pace in heat.",
                        "High humidity (68.2%) impairs cooling. Reduce pace by 10-20s/mile on humid days.",
                        "Train early morning (5-7am) or evening (7-9pm) to avoid peak heat."
                    ]
                ),
                vo2maxEstimate: VO2MaxEstimate(
                    vo2Max: 52.3,
                    fitnessLevel: "good",
                    estimationMethod: "race_performance",
                    vvo2MaxPace: "4:15",
                    racePredictions: [
                        RacePrediction(distance: "5K", distanceKm: 5.0, predictedTime: "0:21:45", predictedTimeSeconds: 1305, pacePerKm: "4:21", pacePerMile: "6:59", confidence: "high"),
                        RacePrediction(distance: "10K", distanceKm: 10.0, predictedTime: "0:45:30", predictedTimeSeconds: 2730, pacePerKm: "4:33", pacePerMile: "7:20", confidence: "high"),
                        RacePrediction(distance: "Half Marathon", distanceKm: 21.0975, predictedTime: "1:42:15", predictedTimeSeconds: 6135, pacePerKm: "4:51", pacePerMile: "7:48", confidence: "medium"),
                        RacePrediction(distance: "Marathon", distanceKm: 42.195, predictedTime: "3:35:45", predictedTimeSeconds: 12945, pacePerKm: "5:06", pacePerMile: "8:13", confidence: "medium")
                    ],
                    recommendations: [
                        "Your estimated VO2 max of 52.3 ml/kg/min places you in the 'good' category for runners.",
                        "Improve VO2 max with interval sessions: 5x1000m at 5K pace with 3min rest."
                    ],
                    dataQualityScore: 0.85
                ),
                trainingLoad: TrainingLoadAnalysis(
                    acuteLoad7Days: 285.3,
                    chronicLoad28Days: 312.8,
                    acwr: 0.91,
                    weeklyTss: 285.3,
                    totalVolumeKm: 45.2,
                    recoveryStatus: "adequate",
                    injuryRiskLevel: "low",
                    trainingTrend: "steady",
                    fitnessTrend: "improving",
                    recommendations: [
                        "✓ ACWR is 0.91 (optimal zone). Training load is well-managed.",
                        "Recovery essentials: 7-9 hours sleep, protein within 30min post-run."
                    ],
                    dailyRecommendations: [
                        "Day 1": "40min easy run",
                        "Day 2": "45min moderate run with 5x2min pickups",
                        "Day 3": "30min recovery run",
                        "Day 4": "50min tempo run (15min at threshold)",
                        "Day 5": "Rest",
                        "Day 6": "40min easy run",
                        "Day 7": "75min long run (easy pace)"
                    ]
                )
            ),
            priorityRecommendations: [
                "✓ ACWR is 0.91 (optimal zone). Training load is well-managed. Continue current progression.",
                "Your estimated VO2 max of 52.3 ml/kg/min places you in the 'good' category for runners.",
                "Average training temperature (24.5°C) is above ideal. Expect 15s/mile slower pace in heat.",
                "Recovery essentials: 7-9 hours sleep, protein within 30min post-run, foam rolling.",
                "Improve VO2 max with interval sessions: 5x1000m at 5K pace with 3min rest."
            ]
        )
    }
}
```

Good luck! Let me know if you have any questions. 🚀
