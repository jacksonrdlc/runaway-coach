#!/bin/bash
# Pre-deployment checklist script

set -e

echo "================================================================================"
echo "RUNAWAY COACH API - PRE-DEPLOYMENT CHECKLIST"
echo "================================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check() {
    local status=$?
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        return 1
    fi
}

# Success check
check_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Check GCloud CLI
echo "1. Checking Google Cloud CLI..."
gcloud --version > /dev/null 2>&1
check "gcloud CLI installed"

# 2. Check project
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    echo -e "${RED}✗${NC} No GCP project configured"
    echo "  Run: gcloud config set project hermes-2024"
    exit 1
else
    check_ok "GCP project: $PROJECT"
fi

# 3. Check authentication
gcloud auth list --filter=status:ACTIVE --format="value(account)" > /dev/null 2>&1
check "GCP authentication active"

# 4. Check required secrets
echo ""
echo "2. Checking Google Secret Manager secrets..."
REQUIRED_SECRETS=(
    "runaway-anthropic-key"
    "runaway-supabase-service"
    "runaway-supabase-jwt-secret"
    "runaway-api-secret"
    "runaway-swift-api-key"
)

for SECRET in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe $SECRET > /dev/null 2>&1; then
        check "$SECRET exists"
    else
        echo -e "${RED}✗${NC} $SECRET missing"
        echo "  Create with: echo -n \"value\" | gcloud secrets create $SECRET --data-file=- --replication-policy=automatic"
    fi
done

# 5. Check Dockerfile
echo ""
echo "3. Checking Dockerfile..."
if [ -f "dockerfile" ]; then
    check "Dockerfile exists"
else
    echo -e "${RED}✗${NC} Dockerfile not found"
    exit 1
fi

# 6. Check cloudbuild.yaml
echo ""
echo "4. Checking cloudbuild.yaml..."
if [ -f "cloudbuild.yaml" ]; then
    check "cloudbuild.yaml exists"

    # Check for JWT secret in cloudbuild.yaml
    if grep -q "SUPABASE_JWT_SECRET" cloudbuild.yaml; then
        check "JWT secret configured in cloudbuild.yaml"
    else
        warn "JWT secret not found in cloudbuild.yaml"
        echo "  Add: SUPABASE_JWT_SECRET=runaway-supabase-jwt-secret:latest"
    fi
else
    echo -e "${RED}✗${NC} cloudbuild.yaml not found"
    exit 1
fi

# 7. Check .env file
echo ""
echo "5. Checking local .env configuration..."
if [ -f ".env" ]; then
    check ".env file exists"

    # Check for required variables
    if grep -q "SUPABASE_JWT_SECRET" .env; then
        check "SUPABASE_JWT_SECRET in .env"
    else
        warn "SUPABASE_JWT_SECRET not in .env"
    fi

    if grep -q "ENVIRONMENT" .env; then
        ENV_VALUE=$(grep "ENVIRONMENT" .env | cut -d '=' -f 2 | tr -d '"' | tr -d "'" | xargs)
        check "ENVIRONMENT set to: $ENV_VALUE"
    else
        warn "ENVIRONMENT not set in .env"
    fi
else
    warn ".env file not found (optional for deployment)"
fi

# 8. Check requirements.txt
echo ""
echo "6. Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    check "requirements.txt exists"

    if grep -q "PyJWT" requirements.txt; then
        check "PyJWT in requirements.txt"
    else
        warn "PyJWT not in requirements.txt (needed for JWT auth)"
    fi
else
    echo -e "${RED}✗${NC} requirements.txt not found"
    exit 1
fi

# 9. Check API endpoints
echo ""
echo "7. Testing local API (if running)..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    check "Local API responding at http://localhost:8000"

    # Test JWT auth module
    if python -c "from utils.auth import get_supabase_auth; get_supabase_auth()" 2>/dev/null; then
        check "JWT auth module imports successfully"
    else
        echo -e "${RED}✗${NC} JWT auth module import failed"
    fi
else
    warn "Local API not running (optional)"
fi

# 10. Check Git status
echo ""
echo "8. Checking Git status..."
if [ -d ".git" ]; then
    check "Git repository initialized"

    # Check for uncommitted changes
    if git diff --quiet && git diff --staged --quiet; then
        check "No uncommitted changes"
    else
        warn "Uncommitted changes detected"
        echo "  Commit changes before deploying"
    fi

    # Check current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ "$BRANCH" = "main" ]; then
        check "On main branch"
    else
        warn "Not on main branch (current: $BRANCH)"
    fi
else
    warn "Not a Git repository"
fi

# Summary
echo ""
echo "================================================================================"
echo "PRE-DEPLOYMENT CHECKLIST COMPLETE"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Review any warnings above"
echo "  2. Deploy with: gcloud builds submit --config=cloudbuild.yaml"
echo "  3. Monitor deployment: gcloud builds list --limit=1"
echo "  4. Test production: curl \$SERVICE_URL/health"
echo ""
echo "Documentation:"
echo "  - documentation/PRODUCTION_DEPLOYMENT.md"
echo "  - documentation/AUTHENTICATION_GUIDE.md"
echo ""