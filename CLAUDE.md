# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Runaway Coach is an AI-powered running coach API built with FastAPI, using Claude API (Anthropic) and LangGraph for agentic workflows. The system provides comprehensive running analysis, personalized recommendations, and intelligent coaching through specialized AI agents designed for iOS app integration.

## Development Commands

### Running the Application
```bash
# Start the API server with hot reload
python -m uvicorn api.main:app --reload

# Alternative: run directly from main.py
python api/main.py

# Run on custom host/port (configured via .env)
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=runaway_coach

# Run specific test file
python test_anthropic.py
python test_startup.py
python test_config.py
```

### Docker & Cloud Deployment
```bash
# Build Docker image
docker build -t runaway-coach .

# Run container with .env file
docker run -p 8000:8000 --env-file .env runaway-coach

# Google Cloud Build (with environment setup)
gcloud builds submit --config cloudbuild.yaml

# Deploy to Cloud Run
gcloud run deploy runaway-coach --image gcr.io/YOUR-PROJECT/runaway-coach --platform managed
```

## Architecture

### Core Agent System

The application uses a **multi-agent architecture** orchestrated by LangGraph workflows:

1. **Supervisor Agent** (`core/agents/supervisor_agent.py`)
   - Main orchestrator for all analysis operations
   - Coordinates other specialized agents
   - Uses direct Anthropic SDK (AsyncAnthropic) for Claude API calls
   - Falls back to rule-based analysis if Claude API unavailable

2. **LangGraph Workflow** (`core/workflows/runner_analysis_workflow.py`)
   - Sequential workflow: Performance → Goal → Pace → Workout → Synthesis
   - Each node is an async operation that updates shared state
   - State type: `RunnerAnalysisState` (TypedDict with metrics, recommendations, processing times)
   - Workflow is compiled at initialization and invoked with `app.ainvoke(initial_state)`

3. **Specialized Agents** (all in `core/agents/`)
   - **PerformanceAnalysisAgent**: Analyzes trends, calculates metrics (mileage, pace, consistency)
   - **GoalStrategyAgent**: Assesses goal feasibility, progress tracking, timeline adjustments
   - **PaceOptimizationAgent**: Zone-based pace recommendations, heart rate mapping
   - **WorkoutPlanningAgent**: Creates personalized workout plans

### Agent Communication Pattern

All agents follow this pattern:
- Load `.env` explicitly via `load_dotenv()`
- Initialize `AsyncAnthropic` client if `ANTHROPIC_API_KEY` available
- Provide AI-powered analysis when client is available
- Fall back to rule-based analysis if Claude API fails
- Return dataclass/dict results that conform to iOS expectations

### API Structure

- **FastAPI Application** (`api/main.py`): Main entry point, middleware, lazy agent initialization
- **Route Modules** (`api/routes/`):
  - `analysis.py`: Runner analysis, quick insights
  - `feedback.py`: Post-workout feedback, pace recommendations
  - `goals.py`: Goal assessment, training plan generation
  - `langgraph.py`: Direct LangGraph workflow endpoints
- **Authentication**: JWT-based via `HTTPBearer`, validates against `SWIFT_APP_API_KEY`

### Data Models

All models defined in `models/__init__.py` using Pydantic v2:
- `Activity`: Run data with distance (float), duration (int seconds), pace (string "MM:SS")
- `RunnerProfile`: User metadata, experience level, weekly mileage, best times
- `WorkoutData`: Combines activity, planned workout, runner profile
- Enums: `WorkoutType`, `PerformanceTrend`, `GoalType`, `GoalStatus`

### Configuration & Settings

- **Settings** (`utils/config.py`): Pydantic Settings class with `.env` file support
- **Required Environment Variables**:
  - `ANTHROPIC_API_KEY`: Claude API key
  - `CLAUDE_MODEL`: Defaults to "claude-3-5-sonnet-20241022"
  - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_ANON_KEY`: Database
  - `SWIFT_APP_API_KEY`: For iOS app authentication
  - `API_SECRET_KEY`, `API_ALGORITHM`: JWT configuration
- **Logger** (`utils/logger.py`): Centralized logging setup

## Critical Implementation Details

### Unit Conversions
- **Storage**: Activities store distance in **meters**, duration in **seconds**
- **Display**: All user-facing recommendations use **MILES** (not kilometers)
- **Conversion**: `distance_miles = (distance_meters / 1000) * 0.621371`
- **Pace Format**: Always "MM:SS" strings (e.g., "8:15" for 8:15/mile pace)

### Claude API Usage
- Model: `claude-3-5-sonnet-20241022`
- All agents use `AsyncAnthropic` for async operations
- Prompts request JSON responses with specific schemas
- JSON parsing includes fallback: find `{` to `}` in response text
- Max tokens: 1000 for most agent operations

### LangGraph State Management
- State is passed through workflow as `RunnerAnalysisState` TypedDict
- Each node updates specific state fields and appends to `completed_steps`
- `processing_times` dict tracks performance of each node
- Final synthesis combines all analysis results into `final_analysis` field

### Error Handling Strategy
- **Graceful Degradation**: All agents have fallback methods
- If Claude API fails → use rule-based analysis
- If LangGraph fails → use simple supervisor analysis
- Always log errors but return valid responses
- HTTP 401 for auth failures, 500 for internal errors

## Development Notes

### iOS Integration Expectations
- Distance measurements must be in miles for user-facing content
- Pace recommendations include ranges (e.g., "6:15-6:45")
- Goal assessments include `key_metrics` with specific schema expected by iOS
- Authentication via Bearer token in Authorization header

### Testing & Debugging
- Test files at root: `test_anthropic.py`, `test_startup.py`, `test_config.py`, `test_goal_schema.py`
- Health check: `GET /health` returns agent status
- Interactive docs: `/docs` (Swagger UI) and `/redoc` (ReDoc)
- Logging configured via `LOG_LEVEL` env var (default: INFO)

### Workflow Visualization
- Get Mermaid diagram: `workflow.get_workflow_graph()` in LangGraph workflow
- State schema: `workflow.get_workflow_state_schema()`

## Important Constraints

- **Lazy Initialization**: Supervisor agent is initialized on first use, not at startup
- **Authentication Required**: All endpoints except `/` and `/health` require valid JWT
- **Async Operations**: All agent methods are async (use `await`)
- **CORS**: Configured to allow all origins (adjust for production)
- **Rate Limiting**: Not currently implemented