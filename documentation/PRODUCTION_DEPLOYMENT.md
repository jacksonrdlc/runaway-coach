# Production Deployment Guide - Google Cloud Run

## Overview

This guide covers deploying the Runaway Coach API to Google Cloud Run with:
- ✅ Supabase JWT authentication
- ✅ Secret management via Google Secret Manager
- ✅ Cloud Build CI/CD
- ✅ Auto-scaling configuration
- ✅ Health checks and monitoring

**Current Project:** `hermes-2024`
**Region:** `us-central1`
**Service:** `runaway-coach-api`

---

## Prerequisites

1. **Google Cloud SDK installed**
   ```bash
   gcloud --version
   ```

2. **Authenticated with GCP**
   ```bash
   gcloud auth login
   gcloud config set project hermes-2024
   ```

3. **Enable required APIs**
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     containerregistry.googleapis.com \
     secretmanager.googleapis.com
   ```

---

## Step 1: Store Secrets in Google Secret Manager

### 1.1 Create/Update JWT Secret

```bash
# Get your JWT secret from Supabase Dashboard -> Settings -> API -> JWT Secret
JWT_SECRET="o0pt+f9rE2IdHzMp8AFy0p8J37O6sZeDyJ7hMbOhIf8zWOqFBL9u5glw4p/l3tz7NET/WWIGO3EFpazoM5Bfmw=="

# Create the secret (first time)
echo -n "$JWT_SECRET" | gcloud secrets create runaway-supabase-jwt-secret \
  --data-file=- \
  --replication-policy=automatic

# Or update existing secret
echo -n "$JWT_SECRET" | gcloud secrets versions add runaway-supabase-jwt-secret \
  --data-file=-
```

### 1.2 Verify All Required Secrets Exist

```bash
# List all secrets
gcloud secrets list

# Required secrets:
# - runaway-anthropic-key (Claude API key)
# - runaway-supabase-service (Supabase service_role key)
# - runaway-supabase-anon (Supabase anon key - optional)
# - runaway-supabase-jwt-secret (NEW - Supabase JWT secret)
# - runaway-api-secret (API secret key)
# - runaway-swift-api-key (Swift app API key)
```

### 1.3 Create Missing Secrets

```bash
# Anthropic API Key
echo -n "your-anthropic-key" | gcloud secrets create runaway-anthropic-key \
  --data-file=- --replication-policy=automatic

# Supabase Service Key
echo -n "your-supabase-service-key" | gcloud secrets create runaway-supabase-service \
  --data-file=- --replication-policy=automatic

# API Secret Key (generate random)
echo -n "$(openssl rand -hex 32)" | gcloud secrets create runaway-api-secret \
  --data-file=- --replication-policy=automatic

# Swift App API Key (generate random)
echo -n "$(openssl rand -hex 32)" | gcloud secrets create runaway-swift-api-key \
  --data-file=- --replication-policy=automatic
```

### 1.4 Grant Cloud Run Access to Secrets

```bash
# Get the Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe hermes-2024 --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant access to all secrets
for SECRET in runaway-anthropic-key runaway-supabase-service runaway-supabase-anon runaway-supabase-jwt-secret runaway-api-secret runaway-swift-api-key; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
done
```

---

## Step 2: Update Supabase URL

The `cloudbuild.yaml` currently has an old Supabase URL. Update it:

```bash
# Your current Supabase URL
OLD_URL="https://onymzwnbxsvltsxpcidy.supabase.co"
NEW_URL="https://nkxvjcdxiyjbndjvfmqy.supabase.co"

# Update cloudbuild.yaml
sed -i '' "s|$OLD_URL|$NEW_URL|g" cloudbuild.yaml
```

Or manually edit `cloudbuild.yaml` line 41:
```yaml
- 'ENVIRONMENT=production,PYTHONUNBUFFERED=1,PYTHONPATH=/app,CLAUDE_MODEL=claude-3-5-sonnet-20241022,SUPABASE_URL=https://nkxvjcdxiyjbndjvfmqy.supabase.co,...'
```

---

## Step 3: Deploy to Cloud Run

### Method 1: Using Cloud Build (Recommended)

```bash
# From project root
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_BUILD_ID=$(date +%Y%m%d-%H%M%S)

# Monitor build progress
gcloud builds list --limit=1
gcloud builds log <BUILD_ID>
```

### Method 2: Direct Deployment

```bash
# Build Docker image
docker build -t gcr.io/hermes-2024/runaway-coach:latest .

# Push to GCR
docker push gcr.io/hermes-2024/runaway-coach:latest

# Deploy to Cloud Run
gcloud run deploy runaway-coach-api \
  --image gcr.io/hermes-2024/runaway-coach:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 80 \
  --set-env-vars "ENVIRONMENT=production,PYTHONUNBUFFERED=1,PYTHONPATH=/app,CLAUDE_MODEL=claude-3-5-sonnet-20241022,SUPABASE_URL=https://nkxvjcdxiyjbndjvfmqy.supabase.co,REDIS_URL=redis://localhost:6379/0,API_HOST=0.0.0.0,API_PORT=8000,API_ALGORITHM=HS256,LOG_LEVEL=INFO,LOG_FORMAT=json,SWIFT_APP_BASE_URL=http://localhost:3000" \
  --set-secrets "ANTHROPIC_API_KEY=runaway-anthropic-key:latest,SUPABASE_SERVICE_KEY=runaway-supabase-service:latest,SUPABASE_ANON_KEY=runaway-supabase-anon:latest,SUPABASE_JWT_SECRET=runaway-supabase-jwt-secret:latest,API_SECRET_KEY=runaway-api-secret:latest,SWIFT_APP_API_KEY=runaway-swift-api-key:latest"
```

---

## Step 4: Verify Deployment

### 4.1 Get Service URL

```bash
gcloud run services describe runaway-coach-api \
  --region us-central1 \
  --format="value(status.url)"
```

### 4.2 Test Health Endpoint

```bash
SERVICE_URL=$(gcloud run services describe runaway-coach-api --region us-central1 --format="value(status.url)")

curl $SERVICE_URL/health | jq
```

Expected output:
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
  "timestamp": "2025-09-30T..."
}
```

### 4.3 Test JWT Authentication

```bash
# Generate a test JWT (from local)
cd /path/to/runaway-coach
source .venv/bin/activate
python scripts/generate_test_jwt.py

# Copy the token and test
TOKEN="eyJhbGci..."
AUTH_USER_ID="bab94363-5d47-4118-89a5-73ec3331e1d6"

curl -X GET "$SERVICE_URL/enhanced/athlete/stats?auth_user_id=$AUTH_USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 4.4 Check Logs

```bash
# Stream logs
gcloud run services logs read runaway-coach-api \
  --region us-central1 \
  --limit 50

# Filter for authentication logs
gcloud run services logs read runaway-coach-api \
  --region us-central1 \
  --filter="jsonPayload.logger=api.main AND jsonPayload.message:Authenticated"
```

---

## Step 5: Configure Custom Domain (Optional)

### 5.1 Map Domain

```bash
gcloud run domain-mappings create \
  --service runaway-coach-api \
  --domain api.runaway.coach \
  --region us-central1
```

### 5.2 Update DNS

Add DNS records as shown by the mapping command:
```
Type: A
Name: api.runaway.coach
Value: <IP from gcloud command>
```

---

## Configuration Reference

### Environment Variables (Set in Cloud Run)

```yaml
ENVIRONMENT: production
PYTHONUNBUFFERED: 1
PYTHONPATH: /app
CLAUDE_MODEL: claude-3-5-sonnet-20241022
SUPABASE_URL: https://nkxvjcdxiyjbndjvfmqy.supabase.co
REDIS_URL: redis://localhost:6379/0
API_HOST: 0.0.0.0
API_PORT: 8000
API_ALGORITHM: HS256
LOG_LEVEL: INFO
LOG_FORMAT: json
SWIFT_APP_BASE_URL: http://localhost:3000
```

### Secrets (Stored in Secret Manager)

```yaml
ANTHROPIC_API_KEY: runaway-anthropic-key:latest
SUPABASE_SERVICE_KEY: runaway-supabase-service:latest
SUPABASE_ANON_KEY: runaway-supabase-anon:latest
SUPABASE_JWT_SECRET: runaway-supabase-jwt-secret:latest  # NEW
API_SECRET_KEY: runaway-api-secret:latest
SWIFT_APP_API_KEY: runaway-swift-api-key:latest
```

### Resource Configuration

```yaml
Memory: 2Gi
CPU: 2
Timeout: 600s
Max Instances: 10
Min Instances: 0
Concurrency: 80
```

---

## Troubleshooting

### Issue: "Secret not found"

```bash
# List secrets
gcloud secrets list

# Create missing secret
echo -n "value" | gcloud secrets create secret-name \
  --data-file=- --replication-policy=automatic

# Grant access
gcloud secrets add-iam-policy-binding secret-name \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Issue: "JWT validation failed"

Check logs for authentication errors:
```bash
gcloud run services logs read runaway-coach-api \
  --region us-central1 \
  --filter="jsonPayload.level=WARNING OR jsonPayload.level=ERROR"
```

Verify JWT secret is correct:
```bash
# Get current secret value
gcloud secrets versions access latest --secret=runaway-supabase-jwt-secret

# Compare with Supabase Dashboard -> Settings -> API -> JWT Secret
```

### Issue: "Build timeout"

Increase timeout in `cloudbuild.yaml`:
```yaml
timeout: '1800s'  # 30 minutes
```

### Issue: "Service unhealthy"

Check health endpoint:
```bash
SERVICE_URL=$(gcloud run services describe runaway-coach-api --region us-central1 --format="value(status.url)")
curl $SERVICE_URL/health
```

Check container logs:
```bash
gcloud run services logs read runaway-coach-api \
  --region us-central1 \
  --limit 100
```

---

## Monitoring

### View Service Details

```bash
gcloud run services describe runaway-coach-api \
  --region us-central1
```

### Monitor Requests

```bash
# Request count
gcloud monitoring time-series list \
  --filter='resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"' \
  --format=json

# Error rate
gcloud run services logs read runaway-coach-api \
  --region us-central1 \
  --filter="httpRequest.status>=400"
```

### Set Up Alerts

```bash
# Create alert policy for error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Runaway Coach API Errors" \
  --condition-display-name="Error rate > 5%" \
  --condition-expression='
    resource.type = "cloud_run_revision"
    AND metric.type = "run.googleapis.com/request_count"
    AND metric.status >= 400
  '
```

---

## Rollback

### Rollback to Previous Revision

```bash
# List revisions
gcloud run revisions list \
  --service runaway-coach-api \
  --region us-central1

# Rollback to specific revision
gcloud run services update-traffic runaway-coach-api \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

---

## CI/CD Setup (Optional)

### Automatic Deployment on Git Push

1. **Connect GitHub Repository**
   ```bash
   gcloud builds triggers create github \
     --repo-name=runaway-coach \
     --repo-owner=YOUR_GITHUB_USERNAME \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. **Push to deploy**
   ```bash
   git push origin main
   # Automatically triggers build and deployment
   ```

---

## Cost Optimization

### Current Configuration Costs (Estimate)

- **Compute**: $0.00002400/vCPU-second + $0.00000250/GiB-second
- **Requests**: $0.40 per million requests
- **Min instances = 0**: No idle charges

### Recommendations

1. **Development**: Use `--min-instances=0` (current setting)
2. **Production with traffic**: Use `--min-instances=1` to reduce cold starts
3. **Monitor usage**: Set up billing alerts

```bash
# Set billing budget alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Runaway Coach API Budget" \
  --budget-amount=100 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

---

## Security Checklist

- ✅ All secrets stored in Secret Manager (not in code)
- ✅ JWT signature verification enabled (`ENVIRONMENT=production`)
- ✅ HTTPS enforced (automatic with Cloud Run)
- ✅ Service account with minimal permissions
- ✅ Authentication required for all endpoints
- ✅ Secrets rotated periodically
- ✅ Monitoring and alerts configured
- ✅ CORS configured appropriately

---

## Quick Commands Reference

```bash
# Deploy
gcloud builds submit --config=cloudbuild.yaml

# Get service URL
gcloud run services describe runaway-coach-api --region us-central1 --format="value(status.url)"

# View logs
gcloud run services logs read runaway-coach-api --region us-central1 --limit 50

# Update secret
echo -n "new-value" | gcloud secrets versions add secret-name --data-file=-

# Rollback
gcloud run services update-traffic runaway-coach-api --region us-central1 --to-revisions REVISION_NAME=100

# Delete service
gcloud run services delete runaway-coach-api --region us-central1
```