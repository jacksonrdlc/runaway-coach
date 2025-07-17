#!/bin/bash
# Cloud Run startup script

echo "Starting Runaway Coach API..."
echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"
echo "Python Path: $PYTHONPATH"

# Test configuration before starting
echo "Testing configuration..."
python -c "
import sys
import os
sys.path.insert(0, '/app')
try:
    from utils.config import get_settings
    settings = get_settings()
    print('✅ Configuration loaded successfully')
    print(f'API Port: {settings.API_PORT}')
    print(f'Claude Model: {settings.CLAUDE_MODEL}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Pre-startup checks passed"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 1 \
        --timeout-keep-alive 120 \
        --timeout-graceful-shutdown 30 \
        --log-level info
else
    echo "❌ Pre-startup checks failed"
    exit 1
fi