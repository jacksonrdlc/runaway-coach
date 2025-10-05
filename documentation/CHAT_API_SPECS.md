# Chat API Specifications for iOS

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://runaway-coach-api-203308554831.us-central1.run.app`

---

## Authentication
All endpoints require JWT Bearer token in Authorization header:
```
Authorization: Bearer <supabase_jwt_token>
```

---

## Endpoints

### 1. Send Chat Message

Send a message to the AI running coach and receive a conversational response.

**Endpoint**: `POST /chat/message`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "message": "What should my easy run pace be?",
  "conversation_id": "uuid-optional",
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
    },
    "profile": {
      "age": 32,
      "experience_level": "intermediate"
    }
  }
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's message to the coach |
| `conversation_id` | string (UUID) | No | Existing conversation ID. Omit to start new conversation |
| `context` | object | No | Current user context (activities, goals, profile) |

**Response** (200 OK):
```json
{
  "success": true,
  "message": "For easy runs at your current fitness level, aim for 8:45-9:15 per mile. This should feel comfortable where you can hold a conversation. Based on your recent 5.2 mile run at 8:15 pace, you're running a bit too fast for easy days. Slowing down will help you recover better and build endurance.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "triggered_analysis": null,
  "processing_time": 0.23
}
```

**Response with Triggered Analysis**:
```json
{
  "success": true,
  "message": "I've analyzed your recent training. You're showing strong consistency with 25.5 miles per week. Here's what I found:",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "triggered_analysis": {
    "type": "performance",
    "data": {
      "performance_metrics": {
        "weekly_mileage": 25.5,
        "avg_pace": "8:20",
        "consistency_score": 0.82
      },
      "recommendations": [
        "Add one tempo run per week",
        "Increase long run to 10 miles"
      ]
    }
  },
  "processing_time": 1.45
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Request success status |
| `message` | string | AI coach response |
| `conversation_id` | string (UUID) | Conversation ID for follow-up messages |
| `triggered_analysis` | object? | Analysis results if workflow was invoked |
| `error_message` | string? | Error details if `success: false` |
| `processing_time` | float | Response time in seconds |

**Triggered Analysis Types**:
- `performance` - Performance analysis was run
- `goal` - Goal assessment was run
- `plan` - Training plan was created

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Invalid authentication token"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "success": false,
  "message": "I'm having trouble processing your message right now. Please try again.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "error_message": "Internal server error",
  "processing_time": 0.15
}
```

---

### 2. Get Conversation History

Retrieve full conversation by ID.

**Endpoint**: `GET /chat/conversation/{conversation_id}`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "conversation": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "bab94363-5d47-4118-89a5-73ec3331e1d6",
    "messages": [
      {
        "role": "user",
        "content": "What should my easy run pace be?",
        "timestamp": "2025-10-05T10:30:00.000Z"
      },
      {
        "role": "assistant",
        "content": "For easy runs, aim for 8:45-9:15 per mile...",
        "timestamp": "2025-10-05T10:30:01.234Z"
      }
    ],
    "context": {
      "weekly_mileage": 25.5
    },
    "created_at": "2025-10-05T10:30:00.000Z",
    "updated_at": "2025-10-05T10:30:01.234Z"
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Conversation not found"
}
```

---

### 3. List Conversations

Get recent conversations for current user.

**Endpoint**: `GET /chat/conversations?limit=10`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Max conversations to return |

**Response** (200 OK):
```json
{
  "success": true,
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-10-05T10:30:00.000Z",
      "updated_at": "2025-10-05T14:22:00.000Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "created_at": "2025-10-04T09:15:00.000Z",
      "updated_at": "2025-10-04T09:45:00.000Z"
    }
  ]
}
```

---

### 4. Delete Conversation

Delete a conversation and all its messages.

**Endpoint**: `DELETE /chat/conversation/{conversation_id}`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Conversation deleted"
}
```

---

## Context Object Specification

The `context` object provides the AI with information about the user's current state. All fields are optional but more context = better responses.

```json
{
  "recent_activity": {
    "distance": 5.2,           // miles
    "avg_pace": "8:15",        // MM:SS format
    "duration": 2565,          // seconds
    "date": "2025-10-04T10:30:00Z",
    "heart_rate_avg": 155,     // bpm (optional)
    "elevation_gain": 125.5    // feet (optional)
  },
  "activities": [              // Recent activities for analysis
    {
      "distance": 5.2,
      "avg_pace": "8:15",
      "date": "2025-10-04T10:30:00Z"
    }
  ],
  "weekly_mileage": 25.5,      // Current weekly mileage
  "goal": {
    "type": "race",            // "race", "distance", "fitness"
    "distance": "5K",          // "5K", "10K", "Half", "Marathon"
    "target_time": "22:00",    // MM:SS or HH:MM:SS
    "race_date": "2025-11-15"
  },
  "profile": {
    "age": 32,
    "gender": "male",          // "male", "female", "other"
    "experience_level": "intermediate", // "beginner", "intermediate", "advanced"
    "best_times": {
      "5K": "22:30",
      "10K": "47:15"
    }
  }
}
```

---

## iOS Integration Examples

### Swift - Send Message

```swift
struct ChatRequest: Codable {
    let message: String
    let conversationId: String?
    let context: ChatContext?

    enum CodingKeys: String, CodingKey {
        case message
        case conversationId = "conversation_id"
        case context
    }
}

struct ChatContext: Codable {
    let recentActivity: Activity?
    let weeklyMileage: Double?
    let goal: Goal?

    enum CodingKeys: String, CodingKey {
        case recentActivity = "recent_activity"
        case weeklyMileage = "weekly_mileage"
        case goal
    }
}

struct ChatResponse: Codable {
    let success: Bool
    let message: String
    let conversationId: String
    let triggeredAnalysis: TriggeredAnalysis?
    let errorMessage: String?
    let processingTime: Double

    enum CodingKeys: String, CodingKey {
        case success, message
        case conversationId = "conversation_id"
        case triggeredAnalysis = "triggered_analysis"
        case errorMessage = "error_message"
        case processingTime = "processing_time"
    }
}

struct TriggeredAnalysis: Codable {
    let type: String  // "performance", "goal", "plan"
    let data: [String: Any]
}

func sendChatMessage(
    message: String,
    conversationId: String? = nil,
    context: ChatContext? = nil
) async throws -> ChatResponse {
    let url = URL(string: "\(baseURL)/chat/message")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(jwtToken)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    let chatRequest = ChatRequest(
        message: message,
        conversationId: conversationId,
        context: context
    )
    request.httpBody = try JSONEncoder().encode(chatRequest)

    let (data, response) = try await URLSession.shared.data(for: request)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw ChatError.invalidResponse
    }

    return try JSONDecoder().decode(ChatResponse.self, from: data)
}
```

### Swift - Conversation Flow

```swift
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var conversationId: String?

    func sendMessage(_ text: String) async {
        // Add user message to UI
        messages.append(ChatMessage(role: "user", content: text))

        // Build context from current user state
        let context = ChatContext(
            recentActivity: userState.lastActivity,
            weeklyMileage: userState.weeklyMileage,
            goal: userState.currentGoal
        )

        do {
            let response = try await sendChatMessage(
                message: text,
                conversationId: conversationId,
                context: context
            )

            // Update conversation ID
            conversationId = response.conversationId

            // Add assistant response to UI
            messages.append(ChatMessage(
                role: "assistant",
                content: response.message
            ))

            // Handle triggered analysis if present
            if let analysis = response.triggeredAnalysis {
                handleTriggeredAnalysis(analysis)
            }
        } catch {
            // Handle error
            messages.append(ChatMessage(
                role: "assistant",
                content: "Sorry, I couldn't process that. Please try again."
            ))
        }
    }

    func handleTriggeredAnalysis(_ analysis: TriggeredAnalysis) {
        switch analysis.type {
        case "performance":
            // Navigate to performance detail view
            break
        case "goal":
            // Show goal assessment
            break
        case "plan":
            // Display training plan
            break
        default:
            break
        }
    }
}
```

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Average response time | 150-300ms (chat only) |
| With analysis workflow | 1-3 seconds |
| Max token limit | 1000 tokens per response |
| Rate limiting | None (currently) |

---

## Auto-Analysis Triggers

The chat agent automatically invokes analysis workflows when users say:

**Performance Analysis**:
- "analyze my training"
- "how am i doing"
- "my progress"
- "recent training"
- "last week"

**Goal Assessment**:
- "goal"
- "race plan"
- "can i run [time/distance]"
- "ready for [race]"

**Training Plan**:
- "training plan"
- "workout plan"
- "what should i run"
- "create a plan"

---

## Best Practices

1. **Always include context**: More context = better responses
2. **Persist conversation_id**: Continue conversations by including previous ID
3. **Handle triggered_analysis**: Show detailed views when workflows are invoked
4. **Cache conversations locally**: Reduce API calls by storing message history
5. **Show typing indicators**: Use `processing_time` to estimate response delay
6. **Error handling**: Always handle 401, 404, 500 responses gracefully

---

## Migration Required

Before using chat endpoints, run this SQL in Supabase:

```sql
-- See migrations/001_create_conversations_table.sql
```

Or use Supabase CLI:
```bash
supabase db push migrations/001_create_conversations_table.sql
```
