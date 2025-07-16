# Runaway Coach API 🏃‍♂️

AI-powered running coach using Claude API and agentic workflows. This FastAPI application provides comprehensive running analysis, personalized recommendations, and intelligent coaching through advanced AI agents.

## 🚀 Features

- **🧠 AI-Powered Analysis**: Uses Claude API for intelligent running analysis
- **📊 Performance Tracking**: Comprehensive metrics and trend analysis
- **🎯 Goal Management**: Smart goal setting and progress monitoring
- **🏃‍♂️ Workout Planning**: Personalized workout recommendations
- **⚡ Pace Optimization**: AI-driven pace recommendations
- **📱 Swift Integration**: Built for iOS app integration
- **🔒 Secure Authentication**: JWT-based authentication system

## 📋 Table of Contents

- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [AI Agents](#ai-agents)
- [Authentication](#authentication)
- [Docker Deployment](#docker-deployment)
- [Development](#development)

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- Anthropic API key
- Supabase account (optional)
- Redis (optional, for caching)

### Local Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd runaway-coach
```

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application:**
```bash
python -m uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

## 🔧 Environment Setup

Create a `.env` file with the following variables:

```env
# Anthropic Claude Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-here
API_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Swift App Integration
SWIFT_APP_BASE_URL=http://localhost:3000
SWIFT_APP_API_KEY=your-swift-api-key
```

## 🔌 API Endpoints

### Health & Status

#### `GET /`
Basic health check endpoint.

**Response:**
```json
{
  "message": "Runaway Coach API",
  "version": "0.1.0",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### `GET /health`
Detailed health check with agent status.

**Response:**
```json
{
  "status": "healthy",
  "agents": {
    "supervisor": "active",
    "performance": "active",
    "goal": "active",
    "workout": "active",
    "pace": "active"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Analysis Endpoints

#### `POST /analysis/runner`
Comprehensive runner analysis using AI agents.

**Request Body:**
```json
{
  "user_id": "user123",
  "activities": [
    {
      "id": "activity1",
      "type": "run",
      "distance": 5.0,
      "duration": 1800,
      "avg_pace": "6:00",
      "date": "2024-01-15T08:00:00.000Z",
      "heart_rate_avg": 160,
      "elevation_gain": 50.0
    }
  ],
  "goals": [
    {
      "id": "goal1",
      "type": "race_time",
      "target": "sub 20 minute 5K",
      "deadline": "2024-06-01"
    }
  ],
  "profile": {
    "user_id": "user123",
    "age": 28,
    "gender": "male",
    "experience_level": "intermediate",
    "weekly_mileage": 25.0,
    "best_times": {
      "5K": "20:30",
      "10K": "42:15"
    },
    "preferences": {
      "preferred_workout_types": ["tempo", "intervals"],
      "days_per_week": 4
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "performance_metrics": {
      "weekly_mileage": 25.0,
      "avg_pace": "6:30",
      "consistency_score": 0.85
    },
    "recommendations": [
      "Increase weekly mileage by 15%",
      "Add tempo runs twice per week",
      "Focus on interval training for speed"
    ],
    "ai_insights": "Based on your recent performances...",
    "agent_metadata": {
      "agents_used": ["supervisor", "anthropic_ai"],
      "processing_time": 2.5,
      "llm_available": true,
      "model_used": "claude-3-sonnet-20240229"
    }
  },
  "processing_time": 2.5
}
```

#### `POST /analysis/quick-insights`
Quick performance insights without full analysis.

**Request Body:**
```json
{
  "activities_data": [
    {
      "id": "activity1",
      "distance": 5.0,
      "duration": 1800,
      "avg_pace": "6:00",
      "date": "2024-01-15T08:00:00.000Z"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "insights": {
    "performance_trend": "improving",
    "weekly_mileage": 25.0,
    "consistency": 0.8,
    "key_strengths": [
      "Consistent pacing",
      "Good endurance base",
      "Strong weekly consistency"
    ],
    "top_recommendations": [
      "Add speed work",
      "Increase long run distance",
      "Focus on recovery"
    ]
  }
}
```

### Feedback Endpoints

#### `POST /feedback/workout`
Generate post-workout insights and feedback.

**Request Body:**
```json
{
  "activity": {
    "id": "workout1",
    "type": "run",
    "distance": 8.0,
    "duration": 2400,
    "avg_pace": "5:00",
    "date": "2024-01-15T07:00:00.000Z",
    "heart_rate_avg": 175
  },
  "planned_workout": {
    "type": "tempo",
    "target_pace": "5:30",
    "target_distance": 8.0
  },
  "runner_profile": {
    "user_id": "user123",
    "age": 28,
    "experience_level": "intermediate"
  }
}
```

**Response:**
```json
{
  "success": true,
  "insights": {
    "performance_rating": 8.5,
    "effort_level": "Hard",
    "recommendations": [
      "Excellent pacing throughout the run",
      "Consider adding recovery run tomorrow",
      "Heart rate was in optimal zone"
    ],
    "next_workout_suggestions": [
      "Easy recovery run (6-8 km)",
      "Strength training session",
      "Rest day recommended"
    ]
  },
  "processing_time": 1.2
}
```

#### `POST /feedback/pace-recommendation`
Generate pace recommendations based on recent performance.

**Request Body:**
```json
{
  "activities_data": [
    {
      "distance": 5.0,
      "duration": 1500,
      "avg_pace": "5:00",
      "effort_level": "hard"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "pace_optimization": {
    "current_fitness_level": "Advanced",
    "recommended_paces": [
      {
        "pace_type": "easy",
        "target_pace": "6:30",
        "pace_range": "6:15-6:45",
        "description": "Conversational pace for base building",
        "heart_rate_zone": "Zone 2"
      },
      {
        "pace_type": "tempo",
        "target_pace": "5:15",
        "pace_range": "5:00-5:30",
        "description": "Comfortably hard, sustainable pace",
        "heart_rate_zone": "Zone 3-4"
      }
    ],
    "weekly_pace_distribution": {
      "easy": 0.7,
      "tempo": 0.2,
      "interval": 0.1
    }
  }
}
```

### Goal Management Endpoints

#### `POST /goals/assess`
Assess goal feasibility and progress.

**Request Body:**
```json
{
  "goals_data": [
    {
      "id": "goal1",
      "type": "race_time",
      "target": "sub 20 minute 5K",
      "deadline": "2024-06-01",
      "current_best": "20:30"
    }
  ],
  "activities_data": [
    {
      "distance": 5.0,
      "duration": 1230,
      "date": "2024-01-15"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "goal_assessments": [
    {
      "goal_id": "goal1",
      "goal_type": "race_time",
      "current_status": "on_track",
      "progress_percentage": 65.0,
      "feasibility_score": 0.8,
      "recommendations": [
        "Increase weekly mileage by 15%",
        "Add tempo runs twice weekly",
        "Focus on 5K pace intervals"
      ],
      "timeline_adjustments": [
        "Goal achievable in current timeline",
        "Consider adding 2 weeks for optimal preparation"
      ],
      "key_metrics": {
        "current_pace": "6:10",
        "target_pace": "6:26",
        "weekly_mileage": 25.0,
        "target_mileage": 35.0
      }
    }
  ]
}
```

#### `POST /goals/training-plan`
Generate a comprehensive training plan for a specific goal.

**Request Body:**
```json
{
  "goal_data": {
    "type": "race_time",
    "target": "sub 20 minute 5K",
    "deadline": "2024-06-01"
  },
  "activities_data": [
    {
      "distance": 5.0,
      "duration": 1230,
      "recent_performance": true
    }
  ],
  "plan_duration_weeks": 12
}
```

**Response:**
```json
{
  "success": true,
  "training_plan": {
    "goal": {
      "type": "race_time",
      "target": "sub 20 minute 5K"
    },
    "duration_weeks": 12,
    "weekly_schedule": [
      {
        "week": 1,
        "workouts": [
          {
            "workout_type": "easy_run",
            "duration_minutes": 45,
            "distance_km": 8.0,
            "target_pace": "6:30",
            "description": "Easy conversational pace run",
            "scheduled_date": "2024-01-22T07:00:00.000Z"
          },
          {
            "workout_type": "tempo_run",
            "duration_minutes": 35,
            "distance_km": 6.0,
            "target_pace": "5:45",
            "description": "Tempo run at threshold pace",
            "scheduled_date": "2024-01-24T07:00:00.000Z"
          }
        ]
      }
    ]
  }
}
```

## 📊 Data Models

### Core Models

#### `Activity`
```python
{
  "id": str,
  "type": str,
  "distance": float,
  "duration": int,  # seconds
  "avg_pace": str,  # MM:SS format
  "date": datetime,
  "heart_rate_avg": int | None,
  "elevation_gain": float | None
}
```

#### `RunnerProfile`
```python
{
  "user_id": str,
  "age": int,
  "gender": str,
  "experience_level": str,  # "beginner", "intermediate", "advanced"
  "weekly_mileage": float,
  "best_times": dict,  # {"5K": "20:30", "10K": "42:15"}
  "preferences": dict
}
```

#### `WorkoutData`
```python
{
  "activity": Activity,
  "planned_workout": dict | None,
  "runner_profile": RunnerProfile
}
```

## 🤖 AI Agents

The application uses multiple specialized AI agents:

### 1. **Supervisor Agent**
- **Purpose**: Orchestrates overall analysis and coordinates other agents
- **Capabilities**: 
  - Comprehensive runner analysis
  - AI-powered insights using Claude API
  - Agent coordination and workflow management

### 2. **Performance Analysis Agent**
- **Purpose**: Analyzes running performance and identifies trends
- **Capabilities**:
  - Performance trend analysis (improving/declining/stable)
  - Consistency scoring
  - Strength and weakness identification

### 3. **Workout Planning Agent**
- **Purpose**: Creates personalized workout plans
- **Capabilities**:
  - Workout type recommendations
  - Training plan generation
  - Post-workout analysis and feedback

### 4. **Pace Optimization Agent**
- **Purpose**: Optimizes running paces for different training zones
- **Capabilities**:
  - Zone-based pace recommendations
  - Heart rate zone mapping
  - Training distribution optimization

### 5. **Goal Strategy Agent**
- **Purpose**: Manages goal setting and progress tracking
- **Capabilities**:
  - Goal feasibility assessment
  - Progress tracking and timeline adjustment
  - Strategic training plan development

## 🔐 Authentication

The API uses JWT-based authentication with the following header:

```
Authorization: Bearer <your-jwt-token>
```

All endpoints except `/` and `/health` require authentication.

### Authentication Flow

1. Obtain JWT token from your authentication service
2. Include token in Authorization header
3. Token is validated against `SWIFT_APP_API_KEY`

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t runaway-coach .

# Run the container
docker run -p 8000:8000 --env-file .env runaway-coach
```

### Environment Variables for Docker

```bash
# Required environment variables
ANTHROPIC_API_KEY=your-anthropic-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SWIFT_APP_API_KEY=your-swift-api-key
API_SECRET_KEY=your-secret-key
```

### Cloud Run Deployment

The Dockerfile is optimized for Google Cloud Run:

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR-PROJECT/runaway-coach

# Deploy to Cloud Run
gcloud run deploy runaway-coach \
  --image gcr.io/YOUR-PROJECT/runaway-coach \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🔧 Development

### Project Structure

```
runaway-coach/
├── api/
│   ├── main.py              # FastAPI application
│   └── routes/
│       ├── analysis.py      # Analysis endpoints
│       ├── feedback.py      # Feedback endpoints
│       └── goals.py         # Goal management endpoints
├── core/
│   └── agents/              # AI agent implementations
│       ├── supervisor_agent.py
│       ├── performance_agent.py
│       ├── workout_planning_agent.py
│       ├── pace_optimization_agent.py
│       └── goal_strategy_agent.py
├── models/
│   └── __init__.py          # Pydantic data models
├── utils/
│   ├── config.py            # Configuration management
│   └── logger.py            # Logging setup
├── integrations/
│   ├── supabase_client.py   # Supabase integration
│   └── swift_interface.py   # Swift app interface
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── dockerfile              # Docker configuration
└── .env                    # Environment variables
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=runaway_coach
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📝 API Documentation

Once the application is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the health check endpoint at `/health`
- Examine logs for detailed error information

---

**Built with ❤️ for runners by runners** 🏃‍♂️🏃‍♀️