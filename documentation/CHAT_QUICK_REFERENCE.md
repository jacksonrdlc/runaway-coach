# Chat API Quick Reference

## Endpoint
```
POST https://runaway-coach-api-203308554831.us-central1.run.app/chat/message
```

## Headers
```
Authorization: Bearer <supabase_jwt>
Content-Type: application/json
```

## Minimal Request
```json
{
  "message": "What should my easy run pace be?"
}
```

## Full Request with Context
```json
{
  "message": "Analyze my training",
  "conversation_id": "optional-uuid-for-continuing",
  "context": {
    "recent_activity": {
      "distance": 5.2,
      "avg_pace": "8:15"
    },
    "weekly_mileage": 25.5,
    "goal": {
      "type": "race",
      "distance": "5K",
      "target_time": "22:00",
      "race_date": "2025-11-15"
    }
  }
}
```

## Response
```json
{
  "success": true,
  "message": "AI coach response here...",
  "conversation_id": "550e8400-...",
  "triggered_analysis": {
    "type": "performance|goal|plan",
    "data": { }
  },
  "processing_time": 0.25
}
```

## Swift Example
```swift
struct ChatRequest: Codable {
    let message: String
    let conversationId: String?
    let context: ChatContext?
}

struct ChatResponse: Codable {
    let success: Bool
    let message: String
    let conversationId: String
    let triggeredAnalysis: TriggeredAnalysis?
    let processingTime: Double
}

// Usage
let response = try await sendChatMessage(
    message: "What pace should I run today?",
    conversationId: currentConversationId,
    context: buildContext()
)

conversationId = response.conversationId
messages.append(response.message)
```

## Other Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat/conversation/{id}` | GET | Get full conversation |
| `/chat/conversations?limit=10` | GET | List recent conversations |
| `/chat/conversation/{id}` | DELETE | Delete conversation |

## Auto-Triggers

Chat automatically runs analysis when user says:
- "analyze my..." → Performance analysis
- "goal" / "race plan" → Goal assessment
- "training plan" → Workout plan

Check `triggered_analysis` field in response to show detailed views.

## Performance
- Chat only: ~200ms
- With analysis: ~1-3 seconds
- All distances in miles, paces in MM:SS format
