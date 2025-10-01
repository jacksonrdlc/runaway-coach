# Enhanced Runaway Coach - Deployment & Update Guide

**Version**: 2.0 Enhanced
**Last Updated**: January 2025

This guide walks through deploying the enhanced Runaway Coach API with full Strava data integration.

---

## Prerequisites

### Required Software
- Python 3.9+
- PostgreSQL (via Supabase)
- Redis (optional, for caching)
- Git

### Required Accounts
- Supabase project with Strava data tables
- Anthropic API key (Claude)
- Google Cloud Platform (for Cloud Run deployment)

### Environment Variables
Ensure `.env` file has all required variables:
```bash
# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key
API_ALGORITHM=HS256
SWIFT_APP_API_KEY=your-swift-api-key

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Database Setup

### 1. Verify Required Tables Exist

Run this query in Supabase SQL editor to check:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'athletes',
    'athlete_stats',
    'activities',
    'activity_types',
    'gear',
    'brands',
    'models',
    'running_goals',
    'goals',
    'daily_commitments',
    'segments',
    'routes',
    'starred_segments',
    'starred_routes'
)
ORDER BY table_name;
```

**Expected Result**: All 14 tables should exist.

---

### 2. Create Missing Tables

If any tables are missing, create them:

#### **running_goals** (App-specific goals)
```sql
CREATE TABLE running_goals (
    id BIGSERIAL PRIMARY KEY,
    athlete_id BIGINT NOT NULL REFERENCES athletes(id),
    title VARCHAR NOT NULL,
    goal_type VARCHAR NOT NULL, -- 'race_time', 'distance', 'consistency', 'weekly_mileage'
    target_value NUMERIC NOT NULL,
    deadline TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_completed BOOLEAN DEFAULT FALSE,
    current_progress NUMERIC,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_running_goals_athlete ON running_goals(athlete_id);
CREATE INDEX idx_running_goals_active ON running_goals(athlete_id, is_active);
```

#### **daily_commitments** (Streak tracking)
```sql
CREATE TABLE daily_commitments (
    id BIGSERIAL PRIMARY KEY,
    athlete_id BIGINT NOT NULL REFERENCES athletes(id),
    commitment_date DATE NOT NULL,
    activity_type VARCHAR NOT NULL,
    is_fulfilled BOOLEAN DEFAULT FALSE,
    fulfilled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(athlete_id, commitment_date)
);

CREATE INDEX idx_daily_commitments_athlete ON daily_commitments(athlete_id);
CREATE INDEX idx_daily_commitments_date ON daily_commitments(athlete_id, commitment_date DESC);
```

#### **athlete_stats** (Aggregated statistics)
```sql
CREATE TABLE athlete_stats (
    id BIGSERIAL PRIMARY KEY,
    athlete_id BIGINT NOT NULL REFERENCES athletes(id) UNIQUE,
    count INT DEFAULT 0,
    distance NUMERIC DEFAULT 0,
    moving_time BIGINT DEFAULT 0,
    elapsed_time BIGINT DEFAULT 0,
    elevation_gain NUMERIC DEFAULT 0,
    achievement_count INT DEFAULT 0,
    ytd_distance NUMERIC DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_athlete_stats_athlete ON athlete_stats(athlete_id);
```

---

### 3. Add Missing Columns to Existing Tables

#### **athletes** table needs `auth_user_id`
```sql
-- Check if column exists
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'athletes'
AND column_name = 'auth_user_id';

-- If missing, add it
ALTER TABLE athletes
ADD COLUMN IF NOT EXISTS auth_user_id UUID REFERENCES auth.users(id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_athletes_auth_user
ON athletes(auth_user_id);
```

#### **activities** table needs weather/HR/cadence columns
```sql
-- Check which columns exist
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'activities'
AND column_name IN (
    'weather_condition', 'humidity', 'wind_speed',
    'max_heart_rate', 'average_heart_rate',
    'max_cadence', 'average_cadence',
    'max_watts', 'average_watts', 'weighted_average_watts',
    'max_temperature', 'average_temperature'
);

-- Add missing columns (adjust as needed)
ALTER TABLE activities
ADD COLUMN IF NOT EXISTS weather_condition VARCHAR,
ADD COLUMN IF NOT EXISTS humidity NUMERIC,
ADD COLUMN IF NOT EXISTS wind_speed NUMERIC,
ADD COLUMN IF NOT EXISTS max_heart_rate INT,
ADD COLUMN IF NOT EXISTS average_heart_rate INT,
ADD COLUMN IF NOT EXISTS max_cadence INT,
ADD COLUMN IF NOT EXISTS average_cadence INT,
ADD COLUMN IF NOT EXISTS max_watts INT,
ADD COLUMN IF NOT EXISTS average_watts INT,
ADD COLUMN IF NOT EXISTS weighted_average_watts INT,
ADD COLUMN IF NOT EXISTS max_temperature NUMERIC,
ADD COLUMN IF NOT EXISTS average_temperature NUMERIC;
```

---

### 4. Create Indexes for Performance

```sql
-- Activities indexes
CREATE INDEX IF NOT EXISTS idx_activities_athlete_date
ON activities(athlete_id, activity_date DESC);

CREATE INDEX IF NOT EXISTS idx_activities_gear
ON activities(gear_id);

-- Gear indexes
CREATE INDEX IF NOT EXISTS idx_gear_athlete
ON gear(athlete_id);

-- Goals indexes
CREATE INDEX IF NOT EXISTS idx_goals_athlete
ON goals(athlete_id);

-- Segments indexes
CREATE INDEX IF NOT EXISTS idx_starred_segments_athlete
ON starred_segments(athlete_id);

CREATE INDEX IF NOT EXISTS idx_starred_routes_athlete
ON starred_routes(athlete_id);
```

---

## Local Development Setup

### 1. Clone and Setup Repository

```bash
cd /path/to/runaway-coach
git pull origin main

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 3. Test Database Connection

Create a test script `test_connection.py`:

```python
import asyncio
from integrations.supabase_client import SupabaseClient

async def test():
    client = SupabaseClient()

    # Test basic query
    try:
        result = client.client.table("athletes").select("id, first_name").limit(1).execute()
        print(f"✅ Connection successful! Found {len(result.data)} athletes")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

asyncio.run(test())
```

Run it:
```bash
python test_connection.py
```

---

### 4. Start Local Development Server

```bash
# Start API server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at:
# - http://localhost:8000
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)
```

---

### 5. Test Enhanced Endpoints

#### Test Health Check
```bash
curl http://localhost:8000/health
```

#### Test Athlete Stats
```bash
curl -X GET "http://localhost:8000/enhanced/athlete/stats?auth_user_id=YOUR_UUID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Test Comprehensive Analysis
```bash
curl -X POST "http://localhost:8000/enhanced/analysis/comprehensive" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"auth_user_id": "YOUR_UUID"}'
```

---

## Production Deployment

### Option 1: Google Cloud Run (Recommended)

#### 1. Build and Push Docker Image

```bash
# Ensure you're in the project root
cd /path/to/runaway-coach

# Build image
docker build -t gcr.io/YOUR-PROJECT-ID/runaway-coach:v2.0 .

# Push to Google Container Registry
docker push gcr.io/YOUR-PROJECT-ID/runaway-coach:v2.0
```

#### 2. Deploy to Cloud Run

```bash
gcloud run deploy runaway-coach \
  --image gcr.io/YOUR-PROJECT-ID/runaway-coach:v2.0 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}" \
  --set-env-vars "SUPABASE_URL=${SUPABASE_URL}" \
  --set-env-vars "SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}" \
  --set-env-vars "SWIFT_APP_API_KEY=${SWIFT_APP_API_KEY}" \
  --set-env-vars "API_SECRET_KEY=${API_SECRET_KEY}" \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300
```

#### 3. Use Cloud Build (Automated)

Create `cloudbuild-enhanced.yaml`:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/runaway-coach:$SHORT_SHA', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/runaway-coach:$SHORT_SHA']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'runaway-coach'
      - '--image'
      - 'gcr.io/$PROJECT_ID/runaway-coach:$SHORT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/runaway-coach:$SHORT_SHA'
```

Deploy:
```bash
gcloud builds submit --config cloudbuild-enhanced.yaml
```

---

### Option 2: Docker Compose (Self-Hosted)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

---

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://your-api-url.run.app/health
```

Expected:
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
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

---

### 2. Test Enhanced Endpoints

#### Get Athlete Stats
```bash
curl -X GET "https://your-api-url.run.app/enhanced/athlete/stats?auth_user_id=USER_UUID" \
  -H "Authorization: Bearer TOKEN"
```

#### Run Performance Analysis
```bash
curl -X POST "https://your-api-url.run.app/enhanced/analysis/performance" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "auth_user_id": "USER_UUID",
    "limit": 30
  }'
```

#### Assess Goals
```bash
curl -X POST "https://your-api-url.run.app/enhanced/goals/assess" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"auth_user_id": "USER_UUID"}'
```

#### Plan Workouts
```bash
curl -X POST "https://your-api-url.run.app/enhanced/workouts/plan" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "auth_user_id": "USER_UUID",
    "goal_id": 123,
    "days": 7
  }'
```

---

### 3. Check Logs

#### Cloud Run Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=runaway-coach" \
  --limit 50 \
  --format json
```

#### Docker Logs
```bash
docker-compose logs -f api
```

---

## Monitoring & Observability

### 1. Add Logging

All enhanced endpoints log:
- Request parameters
- Processing times
- Errors with stack traces

Example log entry:
```json
{
  "timestamp": "2025-01-15T10:30:00.000Z",
  "level": "INFO",
  "message": "Enhanced performance analysis completed for athlete 123",
  "athlete_id": 123,
  "activities_analyzed": 30,
  "processing_time": 2.5
}
```

---

### 2. Add Metrics (Optional)

Create `utils/metrics.py`:

```python
from prometheus_client import Counter, Histogram

# Request counters
analysis_requests = Counter(
    'analysis_requests_total',
    'Total analysis requests',
    ['endpoint', 'status']
)

# Processing time histograms
analysis_duration = Histogram(
    'analysis_duration_seconds',
    'Analysis processing time',
    ['endpoint']
)
```

---

### 3. Set Up Alerts

Create alerts in Google Cloud Monitoring:

- **API Errors**: Alert if error rate > 5%
- **Slow Responses**: Alert if p95 latency > 5s
- **Database Errors**: Alert on Supabase connection failures
- **Anthropic API Errors**: Alert if Claude API fails

---

## Rollback Plan

If deployment fails or causes issues:

### 1. Quick Rollback (Cloud Run)

```bash
# List revisions
gcloud run revisions list --service runaway-coach

# Rollback to previous revision
gcloud run services update-traffic runaway-coach \
  --to-revisions PREVIOUS_REVISION=100
```

---

### 2. Database Rollback

If schema changes cause issues:

```sql
-- Drop new tables (if needed)
DROP TABLE IF EXISTS running_goals CASCADE;
DROP TABLE IF EXISTS daily_commitments CASCADE;
DROP TABLE IF EXISTS athlete_stats CASCADE;

-- Remove new columns from activities (if needed)
ALTER TABLE activities
DROP COLUMN IF EXISTS weather_condition,
DROP COLUMN IF EXISTS humidity,
-- ... etc
```

---

### 3. Code Rollback

```bash
git revert HEAD
git push origin main

# Rebuild and redeploy
gcloud builds submit --config cloudbuild.yaml
```

---

## Troubleshooting

### Issue: "Athlete not found"

**Cause**: `auth_user_id` not set or incorrect

**Fix**:
```sql
-- Verify auth_user_id mapping
SELECT id, auth_user_id, first_name, last_name
FROM athletes
WHERE id = YOUR_ATHLETE_ID;

-- Update if missing
UPDATE athletes
SET auth_user_id = 'UUID_FROM_AUTH_USERS'
WHERE id = YOUR_ATHLETE_ID;
```

---

### Issue: "Athlete stats not found"

**Cause**: `athlete_stats` table not populated

**Fix**:
```sql
-- Populate athlete_stats from activities
INSERT INTO athlete_stats (
    athlete_id,
    count,
    distance,
    moving_time,
    elapsed_time,
    elevation_gain,
    ytd_distance
)
SELECT
    athlete_id,
    COUNT(*) as count,
    SUM(distance) as distance,
    SUM(moving_time) as moving_time,
    SUM(elapsed_time) as elapsed_time,
    SUM(elevation_gain) as elevation_gain,
    SUM(CASE WHEN EXTRACT(YEAR FROM activity_date) = EXTRACT(YEAR FROM NOW())
        THEN distance ELSE 0 END) as ytd_distance
FROM activities
GROUP BY athlete_id
ON CONFLICT (athlete_id) DO UPDATE SET
    count = EXCLUDED.count,
    distance = EXCLUDED.distance,
    moving_time = EXCLUDED.moving_time,
    elapsed_time = EXCLUDED.elapsed_time,
    elevation_gain = EXCLUDED.elevation_gain,
    ytd_distance = EXCLUDED.ytd_distance,
    updated_at = NOW();
```

---

### Issue: Enhanced endpoints return 500 errors

**Check**:
1. Environment variables are set
2. Anthropic API key is valid
3. Supabase credentials are correct
4. All required tables exist

**Debug**:
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Test locally
python -m uvicorn api.main:app --reload
```

---

## Success Criteria

Deployment is successful when:

✅ All health checks pass
✅ Enhanced endpoints return data without errors
✅ Goal progress auto-updates in database
✅ Gear health warnings appear correctly
✅ Weather/HR/elevation analysis works
✅ Workflow completes in < 10 seconds
✅ No breaking changes to existing endpoints

---

## Next Steps After Deployment

1. **Update iOS App** - Integrate `/enhanced/*` endpoints
2. **Add Unit Tests** - Test agents and queries
3. **Performance Tuning** - Add caching, optimize queries
4. **Complete PaceOptimizationAgent** - Add HR/weather/terrain pacing
5. **User Feedback** - Monitor usage and gather feedback
6. **Analytics** - Track feature adoption

---

## Support

For issues or questions:
- Check logs: `gcloud logging read`
- Review API docs: `/docs` endpoint
- Consult `IMPLEMENTATION_SUMMARY.md`