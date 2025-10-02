# Nuxt Web Dashboard for Runaway Coach - Implementation Prompt

## Project Overview

Create a modern, lightweight Nuxt 3 web application that visualizes running analytics from the Runaway Coach API. The app should feature beautiful data visualizations, interactive charts, and a responsive design that works seamlessly across desktop, tablet, and mobile devices.

---

## Tech Stack Requirements

### Core Framework
- **Nuxt 3** (latest stable version)
- **Vue 3** with Composition API
- **TypeScript** for type safety
- **Pinia** for state management

### UI & Styling
- **Tailwind CSS** for utility-first styling
- **Headless UI** or **Radix Vue** for accessible components
- **Lucide Icons** or **Heroicons** for iconography
- **Dark mode** support (system preference + manual toggle)

### Data Visualization
- **Chart.js** or **Apache ECharts** for interactive charts
- **D3.js** (optional, for advanced visualizations)
- **vue-chartjs** for Vue integration
- Consider **TresJS** for 3D visualizations (if showing route maps)

### Authentication
- **Supabase Auth** (already configured)
- JWT token-based authentication
- Secure session management

---

## API Integration

### Base URL
```
https://runaway-coach-api-203308554831.us-central1.run.app
```

### Key Endpoints

#### 1. Quick Wins (Primary Dashboard)
```typescript
GET /quick-wins/comprehensive-analysis
Authorization: Bearer {jwt_token}

// Returns all 3 analyses in one call
Response: {
  success: boolean
  athlete_id: string
  analysis_date: string
  analyses: {
    weather_context: WeatherAnalysis
    vo2max_estimate: VO2MaxEstimate
    training_load: TrainingLoadAnalysis
  }
  priority_recommendations: string[]
}
```

#### 2. Enhanced Analysis Endpoints
```typescript
// Athlete profile & stats
GET /enhanced/athlete/stats?auth_user_id={uuid}

// Performance analysis with weather, HR, elevation
POST /enhanced/analysis/performance
Body: { auth_user_id: string, limit: number }

// Goal assessment with progress tracking
POST /enhanced/goals/assess
Body: { auth_user_id: string }

// Workout planning with gear rotation
POST /enhanced/workouts/plan
Body: { auth_user_id: string, goal_id?: number, days: number }

// Gear health analysis
GET /enhanced/gear/health?auth_user_id={uuid}
```

#### 3. Individual Quick Wins Endpoints
```typescript
GET /quick-wins/weather-impact?limit=30
GET /quick-wins/vo2max-estimate?limit=50
GET /quick-wins/training-load?limit=60
```

### API Documentation
Interactive API docs available at:
```
https://runaway-coach-api-203308554831.us-central1.run.app/docs
```

---

## Design System

### Color Palette

#### Base Colors
```css
/* Light Mode */
--bg-primary: #FFFFFF
--bg-secondary: #F9FAFB
--text-primary: #111827
--text-secondary: #6B7280

/* Dark Mode */
--bg-primary: #0F172A
--bg-secondary: #1E293B
--text-primary: #F1F5F9
--text-secondary: #94A3B8
```

#### Semantic Colors
```css
/* Weather Impact */
--weather-minimal: #10B981 (green)
--weather-moderate: #F59E0B (orange)
--weather-significant: #EF4444 (red)
--weather-severe: #A855F7 (purple)

/* Fitness Levels */
--fitness-elite: #8B5CF6 (purple)
--fitness-excellent: #3B82F6 (blue)
--fitness-good: #10B981 (green)
--fitness-average: #F59E0B (orange)
--fitness-below-avg: #6B7280 (gray)

/* ACWR / Injury Risk */
--risk-low: #10B981 (green)
--risk-moderate: #F59E0B (orange)
--risk-high: #EF4444 (red)
--risk-very-high: #A855F7 (purple)

/* Recovery Status */
--recovery-well: #10B981 (green)
--recovery-adequate: #3B82F6 (blue)
--recovery-fatigued: #F59E0B (orange)
--recovery-overreaching: #EF4444 (red)
--recovery-overtrained: #A855F7 (purple)
```

### Typography
```css
/* Headings */
h1: font-size: 2.5rem, font-weight: 800
h2: font-size: 2rem, font-weight: 700
h3: font-size: 1.5rem, font-weight: 600
h4: font-size: 1.25rem, font-weight: 600

/* Body */
body: font-size: 1rem, line-height: 1.5
small: font-size: 0.875rem
caption: font-size: 0.75rem

/* Font Family */
font-family: 'Inter', -apple-system, sans-serif
```

---

## Page Structure

### 1. Dashboard (Home Page) `/`

**Layout**: Hero section + 4-column grid

**Components**:
- **Hero Stats**: Horizontal scrollable cards showing key metrics
  - ACWR (with risk indicator)
  - VO2 Max (with fitness level)
  - Average Temperature (with impact badge)
  - Weekly Volume (km/miles toggle)

- **Priority Recommendations**: Alert-style banner with top 3-5 recommendations

- **Quick Wins Grid**: 3 cards linking to detailed views
  - Weather Impact Card
  - VO2 Max & Race Predictions Card
  - Training Load & Recovery Card

- **7-Day Workout Plan**: Calendar-style view with color-coded workouts

**Visualizations**:
- Line chart: Training load trend (acute vs chronic over 8 weeks)
- Gauge chart: Current ACWR with safe/danger zones
- Sparklines: Quick trends for key metrics

---

### 2. Weather Impact `/weather`

**Components**:
- **Header**: Average temp/humidity with impact score badge
- **Pace Degradation**: Large callout showing seconds/mile slower
- **Heat Acclimation**: 3-dot progress indicator
- **Optimal Training Times**: Time slots with sunrise/sunset icons
- **Recommendations List**: Expandable cards

**Visualizations**:
- **Temperature Chart**: Area chart showing temperature distribution across runs
- **Humidity Chart**: Line chart with comfort zones highlighted
- **Heat Stress Heatmap**: Calendar heatmap showing heat stress days
- **Weather Conditions Pie**: Distribution of ideal vs heat stress runs

**Interactivity**:
- Toggle between Celsius/Fahrenheit
- Date range selector (7/30/90 days)
- Hover tooltips showing specific run details

---

### 3. VO2 Max & Racing `/fitness`

**Components**:
- **VO2 Max Hero**: Large number with fitness level badge
- **Fitness Level Bar**: Horizontal progress bar (Below Avg → Elite)
- **Data Quality Indicator**: Percentage with explanation tooltip
- **vVO2 Max Pace**: Training target callout box

**Visualizations**:
- **Race Predictions Cards**: 4 cards (5K, 10K, Half, Marathon) with:
  - Predicted time (large)
  - Pace per mile
  - Distance
  - Confidence indicator (progress bar)

- **VO2 Max Trend**: Line chart showing estimated VO2 max over time
- **Race Comparison**: Bar chart comparing predicted times to previous bests

**Interactivity**:
- Click race card to see detailed pacing strategy
- Toggle between km/mile pace
- Export race predictions as image/PDF

---

### 4. Training Load `/training`

**Components**:
- **ACWR Gauge**: Circular gauge (0-2.0) with colored zones
- **Zone Indicator**: Horizontal bar showing current position in risk zones
- **Recovery Status**: Large badge with icon and description
- **Training Trends**: Side-by-side badges (Training Trend + Fitness Trend)

**Visualizations**:
- **Load Comparison**: Dual-axis chart (Acute vs Chronic load)
- **TSS Trend**: Area chart showing Training Stress Score over weeks
- **Volume Chart**: Bar chart showing weekly distance/time
- **ACWR History**: Line chart with safe zone highlighted (0.8-1.3)

**7-Day Plan**:
- Interactive calendar view
- Each day shows:
  - Workout type badge (Easy, Tempo, Interval, Long, Rest)
  - Duration
  - Target intensity
  - Color-coded by workout type

**Interactivity**:
- Click workout day to see full description
- Mark workouts as completed (if implementing workout tracking)
- Export plan as calendar invite

---

### 5. Athlete Profile `/profile`

**Components**:
- **Profile Header**: Name, Strava photo, member since
- **Lifetime Stats**: Total distance, activities, elevation, time
- **YTD Stats**: Year-to-date running metrics
- **Best Efforts**: PR times for common distances

**Visualizations**:
- **Activity Heatmap**: GitHub-style contribution graph
- **Distance by Month**: Bar chart
- **Elevation Gain**: Area chart
- **Activity Types**: Pie chart (Run, Workout, Race, etc.)

---

### 6. Goals & Progress `/goals`

**Components**:
- **Active Goals List**: Cards showing each goal with:
  - Goal name & type
  - Progress bar
  - Current status badge
  - Feasibility score
  - Timeline adjustments

- **Goal Recommendations**: AI-powered suggestions

**Visualizations**:
- **Progress Chart**: Line chart showing distance/time toward goal
- **Milestone Timeline**: Visual timeline with checkpoints
- **Predicted Completion**: Date projection based on current trends

---

## Data Models (TypeScript)

```typescript
// Quick Wins Responses
interface QuickWinsResponse {
  success: boolean
  athlete_id: string
  analysis_date: string
  analyses: {
    weather_context: WeatherAnalysis
    vo2max_estimate: VO2MaxEstimate
    training_load: TrainingLoadAnalysis
  }
  priority_recommendations: string[]
}

interface WeatherAnalysis {
  average_temperature_celsius: number
  average_humidity_percent: number
  heat_stress_runs: number
  ideal_condition_runs: number
  weather_impact_score: 'minimal' | 'moderate' | 'significant' | 'severe'
  pace_degradation_seconds_per_mile: number
  heat_acclimation_level: 'none' | 'developing' | 'well-acclimated'
  optimal_training_times: string[]
  recommendations: string[]
  analysis_period: {
    start: string
    end: string
    total_activities_analyzed: number
  }
}

interface VO2MaxEstimate {
  vo2_max: number
  fitness_level: 'elite' | 'excellent' | 'good' | 'average' | 'below_average'
  estimation_method: string
  vvo2_max_pace: string
  race_predictions: RacePrediction[]
  recommendations: string[]
  data_quality_score: number
}

interface RacePrediction {
  distance: string
  distance_km: number
  predicted_time: string
  predicted_time_seconds: number
  pace_per_km: string
  pace_per_mile: string
  confidence: 'high' | 'medium' | 'low'
}

interface TrainingLoadAnalysis {
  acute_load_7_days: number
  chronic_load_28_days: number
  acwr: number
  weekly_tss: number
  total_volume_km: number
  recovery_status: 'well_recovered' | 'adequate' | 'fatigued' | 'overreaching' | 'overtrained'
  injury_risk_level: 'low' | 'moderate' | 'high' | 'very_high'
  training_trend: 'ramping_up' | 'steady' | 'tapering' | 'detraining'
  fitness_trend: 'improving' | 'maintaining' | 'declining'
  recommendations: string[]
  daily_recommendations: Record<string, string>
}

// Enhanced Analysis
interface AthleteStats {
  total_activities: number
  total_distance: {
    meters: number
    km: number
    miles: number
  }
  total_moving_time: {
    seconds: number
    hours: number
  }
  total_elevation_gain: {
    meters: number
    feet: number
  }
  ytd_distance: {
    meters: number
    km: number
    miles: number
  }
  achievement_count: number
  last_updated: string
}

interface GoalAssessment {
  goal_id: number
  goal_type: string
  current_status: string
  progress_percentage: number
  feasibility_score: number
  recommendations: string[]
  timeline_adjustments: string[]
  key_metrics: Record<string, any>
}
```

---

## Composables (Vue 3)

### useQuickWins.ts
```typescript
export const useQuickWins = () => {
  const data = ref<QuickWinsResponse | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const lastUpdated = ref<Date | null>(null)

  const fetchComprehensiveAnalysis = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch('/quick-wins/comprehensive-analysis', {
        baseURL: 'https://runaway-coach-api-203308554831.us-central1.run.app',
        headers: {
          Authorization: `Bearer ${getAuthToken()}`
        }
      })

      data.value = response
      lastUpdated.value = new Date()
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    lastUpdated: readonly(lastUpdated),
    fetchComprehensiveAnalysis
  }
}
```

### useAthleteStats.ts
```typescript
export const useAthleteStats = () => {
  // Similar pattern for enhanced/athlete/stats endpoint
}
```

### useAuth.ts
```typescript
export const useAuth = () => {
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()

  const getAuthToken = async () => {
    const session = await supabase.auth.getSession()
    return session?.data?.session?.access_token
  }

  const signIn = async (email: string, password: string) => {
    return await supabase.auth.signInWithPassword({ email, password })
  }

  const signOut = async () => {
    return await supabase.auth.signOut()
  }

  return {
    user: readonly(user),
    getAuthToken,
    signIn,
    signOut
  }
}
```

---

## Key Features to Implement

### 1. **Real-time Updates**
- WebSocket connection for live activity updates (optional)
- Auto-refresh data every 15 minutes
- Manual refresh button with pull-to-refresh on mobile

### 2. **Responsive Design**
- Mobile-first approach
- Breakpoints:
  - sm: 640px
  - md: 768px
  - lg: 1024px
  - xl: 1280px
- Touch-friendly interactions on mobile
- Optimized chart rendering for small screens

### 3. **Data Caching**
- Cache API responses in Pinia store
- LocalStorage persistence for offline viewing
- Cache expiration: 1 hour
- Show cached data with "Last updated X minutes ago"

### 4. **Loading States**
- Skeleton loaders for all data sections
- Smooth transitions when data loads
- Error states with retry buttons
- Empty states with helpful messages

### 5. **Accessibility**
- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader-friendly chart descriptions
- Color-blind friendly color schemes
- Focus indicators

### 6. **Performance**
- Lazy load chart libraries
- Code splitting by route
- Image optimization
- Debounced API calls
- Virtual scrolling for large lists

### 7. **Unit Toggle**
- Global km/miles preference
- Celsius/Fahrenheit toggle
- Persist preference in localStorage

---

## Chart Examples

### 1. ACWR Gauge (ApexCharts or Chart.js)
```typescript
const acwrGaugeOptions = {
  type: 'radialBar',
  series: [acwr * 50], // 0-2.0 → 0-100%
  colors: [getACWRColor(acwr)],
  plotOptions: {
    radialBar: {
      hollow: {
        size: '70%'
      },
      dataLabels: {
        name: {
          text: 'ACWR'
        },
        value: {
          formatter: (val) => acwr.toFixed(2)
        }
      }
    }
  }
}
```

### 2. Training Load Trend (Line Chart)
```typescript
const trainingLoadData = {
  labels: last8Weeks.map(w => w.label),
  datasets: [
    {
      label: 'Acute Load (7d)',
      data: acuteLoadData,
      borderColor: '#F59E0B',
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      fill: true
    },
    {
      label: 'Chronic Load (28d)',
      data: chronicLoadData,
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true
    }
  ]
}
```

### 3. Race Predictions Bar Chart
```typescript
const racePredictionsChart = {
  labels: ['5K', '10K', 'Half', 'Marathon'],
  datasets: [{
    label: 'Predicted Time (minutes)',
    data: predictions.map(p => p.predicted_time_seconds / 60),
    backgroundColor: predictions.map(p => getConfidenceColor(p.confidence))
  }]
}
```

### 4. Weather Heatmap (Calendar)
```typescript
// Using a library like vue-cal-heatmap or custom D3
const weatherHeatmapData = activities.map(activity => ({
  date: activity.date,
  value: activity.temperature,
  level: getHeatLevel(activity.temperature) // 0-4
}))
```

---

## Authentication Flow

### 1. Login Page (`/login`)
```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
    <div class="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
      <h1 class="text-3xl font-bold mb-6">Runaway Coach</h1>
      <form @submit.prevent="handleLogin">
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          class="w-full mb-4 px-4 py-3 rounded-lg border"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="w-full mb-4 px-4 py-3 rounded-lg border"
        />
        <button
          type="submit"
          class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold"
        >
          Sign In
        </button>
      </form>
    </div>
  </div>
</template>
```

### 2. Protected Routes
```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware(async (to) => {
  const user = useSupabaseUser()

  if (!user.value && to.path !== '/login') {
    return navigateTo('/login')
  }
})
```

---

## File Structure

```
runaway-web/
├── nuxt.config.ts
├── package.json
├── tailwind.config.js
├── app.vue
├── pages/
│   ├── index.vue              # Dashboard
│   ├── login.vue              # Authentication
│   ├── weather.vue            # Weather Impact
│   ├── fitness.vue            # VO2 Max & Racing
│   ├── training.vue           # Training Load
│   ├── profile.vue            # Athlete Profile
│   └── goals.vue              # Goals & Progress
├── components/
│   ├── dashboard/
│   │   ├── HeroStats.vue
│   │   ├── PriorityRecommendations.vue
│   │   └── QuickWinsGrid.vue
│   ├── charts/
│   │   ├── ACWRGauge.vue
│   │   ├── TrainingLoadChart.vue
│   │   ├── WeatherHeatmap.vue
│   │   └── RacePredictionCard.vue
│   ├── weather/
│   │   ├── PaceDegradation.vue
│   │   ├── HeatAcclimation.vue
│   │   └── OptimalTimes.vue
│   ├── training/
│   │   ├── RecoveryStatus.vue
│   │   ├── WorkoutPlan.vue
│   │   └── ZoneIndicator.vue
│   └── ui/
│       ├── Card.vue
│       ├── Badge.vue
│       ├── StatCard.vue
│       └── LoadingSpinner.vue
├── composables/
│   ├── useQuickWins.ts
│   ├── useAthleteStats.ts
│   ├── useAuth.ts
│   └── useUnits.ts
├── stores/
│   ├── quickWins.ts
│   ├── athlete.ts
│   └── preferences.ts
├── types/
│   ├── api.ts
│   ├── athlete.ts
│   └── charts.ts
├── utils/
│   ├── formatters.ts         # Date, pace, distance formatters
│   ├── colors.ts             # Color mapping functions
│   └── chartConfig.ts        # Reusable chart configurations
└── middleware/
    └── auth.ts               # Authentication guard
```

---

## Environment Variables

```bash
# .env
NUXT_PUBLIC_API_BASE_URL=https://runaway-coach-api-203308554831.us-central1.run.app
NUXT_PUBLIC_SUPABASE_URL=your_supabase_url
NUXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_key
```

---

## Success Criteria

### Functional Requirements
✅ User can sign in with Supabase authentication
✅ Dashboard shows all Quick Wins data in one view
✅ Each metric has a dedicated detail page with visualizations
✅ Charts are interactive (hover, zoom, pan where appropriate)
✅ Data refreshes automatically and manually
✅ Responsive design works on mobile, tablet, desktop
✅ Dark mode toggle works throughout app
✅ Unit preferences (km/mi, °C/°F) persist across sessions

### Performance Requirements
✅ Initial page load < 2 seconds
✅ Chart rendering < 500ms
✅ Smooth animations (60 FPS)
✅ Lighthouse score > 90 (Performance, Accessibility, Best Practices)

### UX Requirements
✅ Intuitive navigation
✅ Clear visual hierarchy
✅ Helpful empty states
✅ Graceful error handling
✅ Loading skeletons match final content layout
✅ Accessible to screen readers
✅ Works without JavaScript for critical content

---

## Nice-to-Have Features

1. **Export Capabilities**
   - Export charts as PNG/SVG
   - Download workout plan as PDF
   - Export data as CSV

2. **Comparison Views**
   - Compare current week vs previous week
   - Compare to same period last year
   - Compare to personal bests

3. **Social Features**
   - Share achievements (if public sharing enabled)
   - Compare stats with friends (privacy-aware)

4. **Advanced Analytics**
   - Custom date range selection
   - Filter by activity type
   - Segment analysis (climbing, flat, etc.)

5. **Notifications**
   - Browser notifications for workout reminders
   - Email digest of weekly insights
   - Alert when ACWR enters danger zone

6. **Mobile App** (Future)
   - PWA with offline support
   - Add to home screen
   - Push notifications

---

## Development Approach

1. **Start with Dashboard** - Build the main dashboard first to see all data
2. **Add Authentication** - Implement Supabase auth early
3. **Build Detail Pages** - Create each metric's detail page
4. **Add Charts** - Integrate chart library and create visualizations
5. **Polish UI** - Refine styling, animations, responsiveness
6. **Optimize** - Performance tuning, caching, lazy loading
7. **Test** - Cross-browser, cross-device, accessibility testing

---

## Example Component: ACWR Gauge

```vue
<template>
  <div class="relative w-64 h-64">
    <svg viewBox="0 0 200 200" class="transform -rotate-90">
      <!-- Background circle -->
      <circle
        cx="100"
        cy="100"
        r="80"
        fill="none"
        stroke="currentColor"
        stroke-width="20"
        class="text-gray-200 dark:text-gray-700"
      />

      <!-- ACWR arc -->
      <circle
        cx="100"
        cy="100"
        r="80"
        fill="none"
        :stroke="acwrColor"
        stroke-width="20"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        class="transition-all duration-1000 ease-out"
      />
    </svg>

    <!-- Center content -->
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-5xl font-bold" :style="{ color: acwrColor }">
        {{ acwr.toFixed(2) }}
      </span>
      <span class="text-sm text-gray-500 dark:text-gray-400 mt-2">
        ACWR
      </span>
      <span class="text-xs font-semibold mt-1" :style="{ color: acwrColor }">
        {{ riskLevel.toUpperCase() }} RISK
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  acwr: number
  riskLevel: string
}>()

const radius = 80
const circumference = 2 * Math.PI * radius

const dashOffset = computed(() => {
  const progress = Math.min(props.acwr / 2.0, 1.0)
  return circumference * (1 - progress)
})

const acwrColor = computed(() => {
  switch (props.riskLevel) {
    case 'low': return '#10B981'
    case 'moderate': return '#F59E0B'
    case 'high': return '#EF4444'
    case 'very_high': return '#A855F7'
    default: return '#6B7280'
  }
})
</script>
```

---

## Summary

This prompt provides everything needed to build a production-ready Nuxt 3 web dashboard:

✅ **Complete tech stack** - Nuxt 3, TypeScript, Tailwind, Chart.js
✅ **Full API integration** - All endpoints documented
✅ **6 main pages** - Dashboard, Weather, Fitness, Training, Profile, Goals
✅ **Beautiful visualizations** - 10+ chart types specified
✅ **Responsive design** - Mobile-first approach
✅ **Authentication** - Supabase auth integration
✅ **Type safety** - Complete TypeScript interfaces
✅ **Performance** - Caching, lazy loading, code splitting
✅ **Accessibility** - ARIA, keyboard nav, screen readers

**Estimated Timeline**: 1-2 weeks for MVP, 3-4 weeks for full feature set with polish

Start with the dashboard to see all your running data visualized beautifully, then expand to detail pages for deeper insights! 🚀
