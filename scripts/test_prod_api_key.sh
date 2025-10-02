#!/bin/bash
# Test production API with API key

API_KEY="afa390428e8800601dbdbb2ad0018acd2768d66753a0980275309b28f0bd5eed"

echo "Testing with API key..."
curl -s -X GET "https://runaway-coach-api-203308554831.us-central1.run.app/enhanced/athlete/stats?auth_user_id=bab94363-5d47-4118-89a5-73ec3331e1d6" \
  -H "Authorization: Bearer $API_KEY" | jq
