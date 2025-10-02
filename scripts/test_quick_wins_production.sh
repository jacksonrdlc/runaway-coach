#!/bin/bash
# Test Quick Wins API endpoints in production

API_KEY="afa390428e8800601dbdbb2ad0018acd2768d66753a0980275309b28f0bd5eed"
USER_ID="94451852"  # Athlete ID (not auth_user_id)
BASE_URL="https://runaway-coach-api-203308554831.us-central1.run.app"

echo "Testing Quick Wins Endpoints..."
echo "================================"
echo ""

echo "1. Weather Impact Analysis"
echo "-------------------------"
curl -s "$BASE_URL/quick-wins/weather-impact?user_id=$USER_ID&limit=30" \
  -H "Authorization: Bearer $API_KEY" | python -m json.tool
echo ""
echo ""

echo "2. VO2 Max Estimation"
echo "--------------------"
curl -s "$BASE_URL/quick-wins/vo2max-estimate?user_id=$USER_ID&limit=50" \
  -H "Authorization: Bearer $API_KEY" | python -m json.tool
echo ""
echo ""

echo "3. Training Load Analysis"
echo "-------------------------"
curl -s "$BASE_URL/quick-wins/training-load?user_id=$USER_ID&limit=60" \
  -H "Authorization: Bearer $API_KEY" | python -m json.tool
echo ""
echo ""

echo "4. Comprehensive Analysis (All in One)"
echo "---------------------------------------"
curl -s "$BASE_URL/quick-wins/comprehensive-analysis?user_id=$USER_ID" \
  -H "Authorization: Bearer $API_KEY" | python -m json.tool
echo ""
echo ""

echo "Test complete!"
