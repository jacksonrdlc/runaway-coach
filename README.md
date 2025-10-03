# Runaway Coach API 🏃‍♂️

**AI-Powered Running Analytics Platform**

A comprehensive FastAPI application that provides intelligent running analysis through a multi-agent AI system powered by Claude and LangGraph. Designed for iOS app integration with advanced features that compete with Strava, WHOOP, and Garmin.

[![Production](https://img.shields.io/badge/production-live-success)](https://runaway-coach-api-203308554831.us-central1.run.app)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple)](https://github.com/langchain-ai/langgraph)

---

## 🎯 Overview

Runaway Coach is an intelligent running analytics platform that provides:

- **🌤️ Weather-Adjusted Training** - The only platform that factors heat stress and weather into your training
- **💨 Free VO2 Max & Race Predictions** - What Strava charges $12/mo for
- **⚡ ACWR Injury Prevention** - What WHOOP charges $30/mo for, plus features they don't have
- **🎯 AI-Powered Coaching** - Personalized recommendations from Claude-powered agents
- **📊 LangGraph Workflows** - Parallel execution of specialized agents (30-40% faster)

**Production API**: https://runaway-coach-api-203308554831.us-central1.run.app

---

## 🚀 Quick Start

### 5-Second Test
```bash
# No authentication required
curl https://runaway-coach-api-203308554831.us-central1.run.app/health
```

### Get Your Running Insights
```bash
# Requires authentication
curl -X GET "https://runaway-coach-api-203308554831.us-central1.run.app/quick-wins/comprehensive-analysis" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Interactive API Docs
📚 **Swagger UI**: https://runaway-coach-api-203308554831.us-central1.run.app/docs

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Wins Endpoints](#-quick-wins-endpoints)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [AI Agents](#-ai-agents)
- [Workflow Visualization](#-workflow-visualization)
- [Deployment](#-deployment)
- [iOS Integration](#-ios-integration)

---

## ✨ Key Features

### 🌤️ Weather Impact Analysis
**Unique competitive advantage - no competitor has this**

- Average temperature & humidity analysis
- Heat stress assessment and tracking
- Pace degradation estimates (seconds/mile slower in heat)
- Heat acclimation level monitoring
- Optimal training time recommendations

### 💨 VO2 Max & Race Predictions
**Free alternative to Strava's $12/mo subscription**

- Multi-method VO2 max estimation (3 algorithms)
- Fitness level classification (Elite → Below Average)
- Race time predictions for 4 distances (5K, 10K, Half Marathon, Marathon)
- vVO2 max pace for interval training
- Confidence scoring on predictions

### ⚡ Training Load & ACWR
**Free alternative to WHOOP's $30/mo subscription + unique features**

- Acute:Chronic Workload Ratio (ACWR) - injury prevention metric
- Training Stress Score (TSS) calculation
- Recovery status monitoring
- Injury risk assessment (Low → Very High)
- 7-day personalized workout plan
- Training trend analysis (Ramping/Steady/Tapering)
- Fitness trend tracking (Improving/Maintaining/Declining)

### 🎯 Additional Features

- **Goal Assessment** - Progress tracking with AI-powered feasibility scores
- **Workout Planning** - Personalized plans with gear rotation and segment recommendations
- **Performance Analysis** - Trend detection, consistency scoring, strength identification
- **Pace Optimization** - Zone-based recommendations with heart rate mapping

---

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, high-performance Python web framework
- **Python 3.13** - Latest stable Python
- **Uvicorn** - Lightning-fast ASGI server

### AI & Orchestration
- **Anthropic Claude** - Claude 3.5 Sonnet (latest model)
- **LangGraph** - Multi-agent workflow orchestration
- **LangChain Core** - AI application framework

### Database & Storage
- **Supabase** - PostgreSQL database (hosted)
- **Supabase Auth** - JWT-based authentication
- Full **Strava data model** integration

### External APIs
- **Open-Meteo** - Free weather data (no API key required)
- **Strava API** - Running activity sync (via Supabase)

### Infrastructure
- **Google Cloud Run** - Serverless container platform
- **Google Cloud Build** - CI/CD pipeline
- **Google Secret Manager** - Secure credential storage
- **Docker** - Containerization

### Data & Validation
- **Pydantic v2** - Type-safe data validation
- **Python Dataclasses** - Structured agent responses
- **TypedDict** - Type hints for workflow state

---

## 🏗️ Architecture

### Multi-Agent System

The application uses **8 specialized AI agents** orchestrated by LangGraph:

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│                                                              │
│  Start → Performance Analysis                               │
│             ↓                                                │
│             ├─→ Weather Context ──────┐                     │
│             ├─→ VO2 Max Estimation ───┤                     │
│             ├─→ Training Load ────────┼→ Pace Optimization  │
│             └─→ Goal Assessment ──────┘         ↓           │
│                                          Workout Planning    │
│                                                 ↓            │
│                                          Final Synthesis     │
│                                                 ↓            │
│                                                End           │
└─────────────────────────────────────────────────────────────┘
```

**Key Architectural Features:**
- ⚡ **Parallel Execution** - 4 agents run simultaneously (30-40% faster)
- 🔄 **State Management** - Type-safe state passing between agents
- 🎯 **Specialized Agents** - Each agent focuses on one domain
- 📊 **Observable Workflows** - Built-in Mermaid diagram generation

**See full workflow visualization**: [WORKFLOW_VISUAL.md](WORKFLOW_VISUAL.md)

### Project Structure

```
runaway-coach/
├── api/                          # FastAPI routes
│   ├── main.py                   # Application entry point
│   └── routes/
│       ├── quick_wins.py         # Quick Wins endpoints (Weather, VO2, Load)
│       ├── enhanced_analysis.py  # Enhanced Strava data endpoints
│       ├── analysis.py           # Legacy analysis endpoints
│       ├── feedback.py           # Post-workout feedback
│       ├── goals.py              # Goal management
│       └── langgraph.py          # Direct workflow access
├── core/
│   ├── agents/                   # 8 specialized AI agents
│   │   ├── supervisor_agent.py
│   │   ├── performance_agent.py
│   │   ├── weather_context_agent.py
│   │   ├── vo2max_estimation_agent.py
│   │   ├── training_load_agent.py
│   │   ├── goal_strategy_agent.py
│   │   ├── pace_optimization_agent.py
│   │   └── workout_planning_agent.py
│   └── workflows/                # LangGraph workflows
│       ├── runner_analysis_workflow.py
│       └── enhanced_runner_analysis_workflow.py
├── integrations/                 # External services
│   ├── supabase_client.py
│   └── supabase_queries.py
├── models/                       # Data models
│   ├── __init__.py               # Basic Pydantic models
│   └── strava.py                 # Full Strava data model
├── utils/                        # Utilities
│   ├── config.py                 # Pydantic settings
│   ├── logger.py                 # Logging configuration
│   └── auth.py                   # JWT authentication
├── scripts/                      # Utility scripts
│   ├── visualize_workflow.py     # Generate workflow diagrams
│   └── deploy_check.sh           # Deployment verification
├── tests/                        # Test files
├── documentation/                # Comprehensive docs
│   ├── QUICK_WINS_IMPLEMENTATION.md
│   ├── IOS_CLAUDE_PROMPT.md
│   ├── IOS_FEATURE_SPECS.md
│   └── UPGRADE_PLAN.md
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Production container
├── cloudbuild.yaml              # Google Cloud Build config
└── .env                         # Environment variables
```

---

## 🏆 Quick Wins Endpoints

### Comprehensive Analysis (All-in-One)
```http
GET /quick-wins/comprehensive-analysis
Authorization: Bearer {jwt_token}
```

Returns weather impact + VO2 max + training load in one call.

**Response:**
```json
{
  "success": true,
  "athlete_id": "94451852",
  "analyses": {
    "weather_context": { /* ... */ },
    "vo2max_estimate": { /* ... */ },
    "training_load": { /* ... */ }
  },
  "priority_recommendations": [
    "ACWR is 0.91 (optimal zone). Maintain current training volume.",
    "Your estimated VO2 max of 52.3 ml/kg/min places you in the 'good' category.",
    "Train early morning (5-7am) or evening (7-9pm) to avoid peak heat."
  ]
}
```

### Individual Endpoints

```http
GET /quick-wins/weather-impact?limit=30
GET /quick-wins/vo2max-estimate?limit=50
GET /quick-wins/training-load?limit=60
```

**See full endpoint documentation**: [QUICK_START.md](QUICK_START.md)

---

## 💻 Installation

### Prerequisites

- Python 3.9+ (3.13 recommended)
- Virtual environment
- Anthropic API key
- Supabase account

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/runaway-coach.git
cd runaway-coach
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run the application**
```bash
python -m uvicorn api.main:app --reload
```

API available at: http://localhost:8000

### Required Environment Variables

```env
# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-your-key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# API Configuration
API_SECRET_KEY=your-secret-key
API_ALGORITHM=HS256
API_HOST=0.0.0.0
API_PORT=8000

# Authentication
SWIFT_APP_API_KEY=your-api-key

# Optional
LOG_LEVEL=INFO
```

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: https://runaway-coach-api-203308554831.us-central1.run.app/docs
- **ReDoc**: https://runaway-coach-api-203308554831.us-central1.run.app/redoc

### Health Check

```bash
curl https://runaway-coach-api-203308554831.us-central1.run.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "agents": {
    "supervisor": "active",
    "performance": "active",
    "goal": "active",
    "workout": "active",
    "pace": "active",
    "weather_context": "active",
    "vo2max_estimation": "active",
    "training_load": "active"
  },
  "timestamp": "2025-10-02T17:30:00.000Z"
}
```

### Authentication

All endpoints (except `/` and `/health`) require authentication:

```bash
curl -X GET "https://runaway-coach-api-203308554831.us-central1.run.app/quick-wins/comprehensive-analysis" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Supported authentication methods:**
1. Supabase JWT tokens (recommended)
2. API key (for testing)

---

## 🤖 AI Agents

### 1. 🏃 Performance Analysis Agent
**Analyzes running trends and metrics**

- Weekly mileage calculation
- Consistency scoring (0-1)
- Performance trend detection (improving/declining/stable)
- Strength and weakness identification
- Average pace analysis

### 2. 🌤️ Weather Context Agent
**Unique competitive advantage**

- Temperature and humidity analysis
- Heat stress run detection
- Pace degradation estimation
- Heat acclimation level tracking
- Optimal training time recommendations

**No competitor has this feature!**

### 3. 💨 VO2 Max Estimation Agent
**Multi-method fitness assessment**

- VO2 max estimation (3 algorithms: Jack Daniels, Race Performance, HR-based)
- Fitness level classification (Elite, Excellent, Good, Average, Below Average)
- Race predictions for 5K, 10K, Half Marathon, Marathon
- vVO2 max pace calculation
- Confidence scoring

**Strava charges $12/mo for this - we provide it free!**

### 4. ⚡ Training Load Agent
**Injury prevention and recovery monitoring**

- Acute:Chronic Workload Ratio (ACWR)
- Training Stress Score (TSS)
- Recovery status assessment
- Injury risk classification (Low, Moderate, High, Very High)
- Training trend analysis
- Fitness trend tracking
- 7-day personalized workout plan

**WHOOP charges $30/mo for TSS - we provide more features for free!**

### 5. 🎯 Goal Strategy Agent
**AI-powered goal management**

- Goal feasibility assessment (0-1 score)
- Progress percentage calculation
- Timeline adjustment recommendations
- Key metrics tracking

### 6. 🏃‍♂️ Pace Optimization Agent
**Zone-based training recommendations**

- Heart rate zone mapping
- Pace recommendations by zone
- Training distribution optimization
- Weather-adjusted pacing

### 7. 📅 Workout Planning Agent
**Personalized training plans**

- 7-day workout generation
- Workout type selection (Easy, Tempo, Interval, Long, Rest)
- Duration and intensity targets
- Gear rotation recommendations
- Segment suggestions

### 8. 🎓 Supervisor Agent
**Workflow orchestration**

- Coordinates all agents
- Combines analysis results
- Generates priority recommendations
- Ensures data consistency

---

## 📊 Workflow Visualization

### Generate Flow Diagram

```bash
python scripts/visualize_workflow.py
```

**Generates:**
- `WORKFLOW_DIAGRAM.md` - Auto-generated LangGraph diagram
- `WORKFLOW_VISUAL.md` - Enhanced, colorful visualization with documentation

**View online**: Open the Mermaid diagram at https://mermaid.live

**See detailed visualization**: [WORKFLOW_VISUAL.md](WORKFLOW_VISUAL.md)

---

## 🚀 Deployment

### Google Cloud Run (Production)

**Current production deployment:**
```
https://runaway-coach-api-203308554831.us-central1.run.app
```

**Deploy new version:**
```bash
gcloud builds submit --config cloudbuild.yaml
```

**Configuration:**
- Memory: 2Gi
- CPU: 2
- Timeout: 600s
- Max instances: 10
- Min instances: 0 (scales to zero)
- Cold start: ~3-5 seconds
- Warm response: <1 second

### Docker

**Build:**
```bash
docker build -t runaway-coach .
```

**Run:**
```bash
docker run -p 8000:8000 --env-file .env runaway-coach
```

### Manual Deployment

```bash
# Build and push
gcloud builds submit --tag gcr.io/hermes-2024/runaway-coach

# Deploy
gcloud run deploy runaway-coach-api \
  --image gcr.io/hermes-2024/runaway-coach \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

---

## 📱 iOS Integration

### Complete iOS Implementation Guide

See: [documentation/IOS_CLAUDE_PROMPT.md](documentation/IOS_CLAUDE_PROMPT.md)

**Quick integration:**

```swift
// API Configuration
private let baseURL = "https://runaway-coach-api-203308554831.us-central1.run.app"

// Fetch comprehensive analysis
func fetchQuickWins() async throws -> QuickWinsResponse {
    let url = URL(string: "\(baseURL)/quick-wins/comprehensive-analysis")!
    var request = URLRequest(url: url)
    request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")

    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(QuickWinsResponse.self, from: data)
}
```

**Authentication Fix (October 2025)**:
The API now properly resolves Supabase auth UUIDs to athlete IDs. Your iOS app can continue sending the auth user ID from the JWT token without any code changes.

See: [IOS_AUTH_FIX.md](IOS_AUTH_FIX.md)

---

## 💰 Cost Analysis

### Monthly Costs

| Service | Cost |
|---------|------|
| Open-Meteo API | **$0** (free) |
| Anthropic Claude API | ~$1-3 (usage-based) |
| Google Cloud Run | ~$5-10 (within free tier for moderate use) |
| Supabase | **$0** (free tier) |
| **Total** | **~$5-15/month** |

### Competitive Comparison

| Feature | Runaway Coach | Strava | WHOOP | Garmin |
|---------|---------------|--------|-------|--------|
| Weather Context | ✅ **FREE** | ❌ | ❌ | ❌ |
| VO2 Max & Race Predictions | ✅ **FREE** | $12/mo | ❌ | ✅ Device |
| ACWR Injury Risk | ✅ **FREE** | ❌ | ❌ | ❌ |
| Training Load (TSS) | ✅ **FREE** | ❌ | $30/mo | ✅ Device |
| Heat Acclimation | ✅ **FREE** | ❌ | ❌ | ❌ |
| AI Coaching | ✅ **FREE** | ❌ | ❌ | ❌ |

**You're competitive with or better than premium services at a fraction of the cost!**

---

## 🧪 Testing

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=runaway_coach

# Run specific test
python tests/test_anthropic.py
```

### Production Testing

```bash
# Test comprehensive analysis
./scripts/test_quick_wins_production.sh

# Health check
curl https://runaway-coach-api-203308554831.us-central1.run.app/health
```

---

## 📖 Documentation

- **Quick Start Guide**: [QUICK_START.md](QUICK_START.md)
- **Deployment Success**: [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md)
- **Production Testing**: [PRODUCTION_TESTED.md](PRODUCTION_TESTED.md)
- **iOS Integration**: [IOS_AUTH_FIX.md](IOS_AUTH_FIX.md)
- **Workflow Visualization**: [WORKFLOW_VISUAL.md](WORKFLOW_VISUAL.md)
- **Cleanup Report**: [CLEANUP_REPORT.md](CLEANUP_REPORT.md)
- **Nuxt Web App Prompt**: [NUXT_WEB_APP_PROMPT.md](NUXT_WEB_APP_PROMPT.md)

### Feature Documentation

- [Quick Wins Implementation](documentation/QUICK_WINS_IMPLEMENTATION.md)
- [iOS Feature Specs](documentation/IOS_FEATURE_SPECS.md)
- [Upgrade Plan](documentation/UPGRADE_PLAN.md)

---

## 🔒 Security

- **JWT Authentication** via Supabase Auth
- **API Key Fallback** for testing
- **Secret Management** via Google Cloud Secret Manager
- **No hardcoded secrets** in codebase
- **CORS configured** for iOS app integration

---

## 🐛 Troubleshooting

### Common Issues

**1. "No activities found for user"**
- Ensure you're using the correct user identifier
- API accepts both athlete_id (integer) or auth_user_id (UUID)

**2. "Token expired"**
- Refresh your Supabase JWT token
- Check token expiration time

**3. Empty analyses in comprehensive analysis**
- Verify you have 28+ days of activity data
- Ensure activities have GPS coordinates for weather analysis
- Check that activities include pace/speed data

**4. Slow API response**
- First request after idle may take 3-5s (cold start)
- Subsequent requests are <1s
- Consider Cloud Run min instances if needed

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Anthropic** - For the incredible Claude API
- **LangGraph** - For the powerful workflow orchestration framework
- **Supabase** - For the excellent database and auth platform
- **Open-Meteo** - For free, high-quality weather data
- **Strava** - For inspiration and the original activity data model

---

## 📞 Support

- **API Health**: https://runaway-coach-api-203308554831.us-central1.run.app/health
- **API Docs**: https://runaway-coach-api-203308554831.us-central1.run.app/docs
- **Issues**: Open a GitHub issue
- **Latest Build**: Check Cloud Build console

---

<div align="center">

**Built with ❤️ for runners by runners** 🏃‍♂️🏃‍♀️

**Production**: https://runaway-coach-api-203308554831.us-central1.run.app

[Get Started](QUICK_START.md) | [API Docs](https://runaway-coach-api-203308554831.us-central1.run.app/docs) | [iOS Integration](documentation/IOS_CLAUDE_PROMPT.md)

</div>
