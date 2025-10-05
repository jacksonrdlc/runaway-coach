#!/bin/bash

# Test Chat Endpoint
# Usage: ./test_chat_endpoint.sh [production|local]

ENVIRONMENT=${1:-local}

if [ "$ENVIRONMENT" = "production" ]; then
    BASE_URL="https://runaway-coach-api-203308554831.us-central1.run.app"
    # Use your production JWT token
    TOKEN="YOUR_PRODUCTION_JWT_TOKEN_HERE"
else
    BASE_URL="http://localhost:8000"
    # Use local development token or API key
    TOKEN="YOUR_LOCAL_JWT_TOKEN_HERE"
fi

echo "Testing Chat API on $ENVIRONMENT environment"
echo "Base URL: $BASE_URL"
echo ""

# Test 1: Simple chat message
echo "Test 1: Simple chat message"
echo "----------------------------"
curl -s -X POST "$BASE_URL/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What should my easy run pace be?"
  }' | jq '.'

echo -e "\n\n"

# Test 2: Chat with context
echo "Test 2: Chat message with context"
echo "-----------------------------------"
curl -s -X POST "$BASE_URL/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Based on my recent training, how am I doing?",
    "context": {
      "recent_activity": {
        "distance": 5.2,
        "avg_pace": "8:15",
        "date": "2025-10-04T10:30:00Z"
      },
      "weekly_mileage": 25.5,
      "goal": {
        "type": "race",
        "distance": "5K",
        "target_time": "22:00",
        "race_date": "2025-11-15"
      }
    }
  }' | jq '.'

echo -e "\n\n"

# Test 3: Trigger analysis
echo "Test 3: Message that triggers analysis"
echo "---------------------------------------"
RESPONSE=$(curl -s -X POST "$BASE_URL/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze my recent training and tell me how I can improve",
    "context": {
      "activities": [
        {
          "distance": 5.2,
          "avg_pace": "8:15",
          "date": "2025-10-04T10:30:00Z"
        },
        {
          "distance": 3.1,
          "avg_pace": "8:30",
          "date": "2025-10-03T07:00:00Z"
        }
      ],
      "weekly_mileage": 25.5
    }
  }')

echo "$RESPONSE" | jq '.'

# Extract conversation ID for next test
CONVERSATION_ID=$(echo "$RESPONSE" | jq -r '.conversation_id')

echo -e "\n\n"

# Test 4: Continue conversation
if [ "$CONVERSATION_ID" != "null" ]; then
    echo "Test 4: Continue conversation (ID: $CONVERSATION_ID)"
    echo "----------------------------------------------------"
    curl -s -X POST "$BASE_URL/chat/message" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"message\": \"Thanks! What about my long run this weekend?\",
        \"conversation_id\": \"$CONVERSATION_ID\"
      }" | jq '.'

    echo -e "\n\n"

    # Test 5: Get conversation history
    echo "Test 5: Get conversation history"
    echo "---------------------------------"
    curl -s -X GET "$BASE_URL/chat/conversation/$CONVERSATION_ID" \
      -H "Authorization: Bearer $TOKEN" | jq '.'

    echo -e "\n\n"
fi

# Test 6: List conversations
echo "Test 6: List recent conversations"
echo "-----------------------------------"
curl -s -X GET "$BASE_URL/chat/conversations?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n\n"
echo "Tests complete!"
