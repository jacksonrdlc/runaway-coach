# Authentication Guide - Supabase JWT Implementation

## Overview

The Runaway Coach API supports two authentication methods:

1. **Supabase JWT Tokens** (Recommended for production)
2. **Simple API Key** (Backwards compatibility)

## How It Works

### Authentication Flow

```
1. Client obtains JWT token from Supabase Auth
2. Client includes token in Authorization header
3. API validates token and extracts user information
4. API allows access to protected endpoints
```

### Token Validation

- **Development**: Signature verification is OPTIONAL (for easier testing)
- **Production**: Signature verification is REQUIRED

Set environment: `ENVIRONMENT=production` in `.env`

---

## Setup

### 1. Get Your Supabase JWT Secret

1. Go to your Supabase Dashboard
2. Navigate to: **Settings → API**
3. Copy the **JWT Secret** (NOT the anon key or service_role key)
4. Add to `.env`:

```bash
# In .env file
SUPABASE_JWT_SECRET=your-jwt-secret-here
ENVIRONMENT=production  # or 'development' for local testing
```

### 2. Environment Variables

Required in `.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_JWT_SECRET=your-jwt-secret  # For production JWT validation

# Environment
ENVIRONMENT=development  # or 'production'

# Legacy API Key (for backwards compatibility)
SWIFT_APP_API_KEY=your-api-key
```

---

## Usage

### Method 1: Supabase JWT Token (Recommended)

**From iOS App:**

```swift
// Get current session from Supabase Auth
let session = try await supabase.auth.session
let token = session.accessToken

// Make API request
var request = URLRequest(url: url)
request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
```

**From curl:**

```bash
# Get JWT token from Supabase Auth first
TOKEN="your-jwt-token"

curl -X GET "http://localhost:8000/enhanced/athlete/stats?auth_user_id=uuid-here" \
  -H "Authorization: Bearer $TOKEN"
```

### Method 2: Simple API Key (Legacy)

```bash
curl -X GET "http://localhost:8000/enhanced/athlete/stats?auth_user_id=uuid-here" \
  -H "Authorization: Bearer afa390428e8800601dbdbb2ad0018acd2768d66753a0980275309b28f0bd5eed"
```

---

## Testing Locally

### Generate Test JWT Token

Use the provided script to generate a test JWT token:

```bash
python scripts/generate_test_jwt.py

# Or with custom user:
python scripts/generate_test_jwt.py "user-uuid" "user@email.com"
```

Output:
```
TEST JWT TOKEN GENERATED
================================================================================

User ID: bab94363-5d47-4118-89a5-73ec3331e1d6
Email: jackrudelic@gmail.com
Expires: 24 hours

Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

================================================================================
USAGE
================================================================================

Test with curl:

curl -X GET "http://localhost:8000/enhanced/athlete/stats?auth_user_id=bab94363-5d47-4118-89a5-73ec3331e1d6" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Test JWT Validation

```bash
# Start server
source .venv/bin/activate
python -m uvicorn api.main:app --reload

# Generate test token
TOKEN=$(python scripts/generate_test_jwt.py | grep "eyJ" | tr -d ' ')

# Test endpoint
curl -X GET "http://localhost:8000/enhanced/athlete/stats?auth_user_id=bab94363-5d47-4118-89a5-73ec3331e1d6" \
  -H "Authorization: Bearer $TOKEN"
```

---

## How the API Validates Tokens

### Authentication Flow (api/main.py:get_current_user)

```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    1. Extract token from Authorization header
    2. Try Supabase JWT validation first
    3. Fall back to API key if JWT fails
    4. Return user info or raise 401
    """
    token = credentials.credentials

    # Try JWT validation
    if token != settings.SWIFT_APP_API_KEY:
        user_info = supabase_auth.validate_token(token)
        return user_info  # Contains: user_id, auth_user_id, email, role

    # Fallback to API key
    if token == settings.SWIFT_APP_API_KEY:
        return {"user_id": "api_key_auth", "auth_method": "api_key"}

    # Invalid
    raise HTTPException(status_code=401)
```

### JWT Validation (utils/auth.py:SupabaseAuth)

```python
def decode_token(self, token: str, verify_signature: Optional[bool] = None):
    """
    1. Use environment-based verification (production=True, dev=False)
    2. Decode JWT with PyJWT
    3. Verify expiration (always)
    4. Verify signature (if enabled)
    5. Extract user_id (sub), email, role
    """
    if verify_signature:
        payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
    else:
        payload = jwt.decode(token, options={"verify_signature": False})

    return payload  # Contains: sub, email, role, aud, exp, iat
```

---

## User Information Extracted from JWT

The API extracts the following from validated JWT tokens:

```python
{
    "user_id": "bab94363-5d47-4118-89a5-73ec3331e1d6",  # Supabase user UUID
    "auth_user_id": "bab94363-5d47-4118-89a5-73ec3331e1d6",  # Same as user_id
    "email": "user@example.com",
    "role": "authenticated",
    "aud": "authenticated",
    "exp": 1735603200,  # Expiration timestamp
    "iat": 1735516800   # Issued at timestamp
}
```

---

## iOS App Integration

### 1. Supabase Auth Setup

```swift
import Supabase

let supabase = SupabaseClient(
    supabaseURL: URL(string: "https://your-project.supabase.co")!,
    supabaseKey: "your-anon-key"
)
```

### 2. Sign In User

```swift
// Email/password sign in
try await supabase.auth.signIn(
    email: "user@example.com",
    password: "password"
)

// Get session
let session = try await supabase.auth.session
let accessToken = session.accessToken
let userId = session.user.id.uuidString
```

### 3. Make Authenticated API Requests

```swift
func fetchAthleteStats(userId: String, token: String) async throws {
    let url = URL(string: "https://api.example.com/enhanced/athlete/stats?auth_user_id=\(userId)")!

    var request = URLRequest(url: url)
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.httpMethod = "GET"

    let (data, response) = try await URLSession.shared.data(for: request)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw APIError.unauthorized
    }

    let athleteStats = try JSONDecoder().decode(AthleteStats.self, from: data)
    return athleteStats
}
```

### 4. Handle Token Refresh

```swift
// Supabase automatically refreshes tokens
// Just get the current session before each request
let session = try await supabase.auth.session
let token = session.accessToken

// Token is automatically refreshed if expired
```

---

## Security Best Practices

### Development

- ✅ Signature verification can be disabled (`ENVIRONMENT=development`)
- ✅ Use test JWT tokens from `scripts/generate_test_jwt.py`
- ✅ API key fallback available for quick testing

### Production

- ✅ **ALWAYS** set `ENVIRONMENT=production`
- ✅ **ALWAYS** set `SUPABASE_JWT_SECRET` in production
- ✅ Use HTTPS only
- ✅ Short token expiration (1-2 hours recommended)
- ✅ Rotate JWT secret periodically
- ⚠️ Never expose JWT secret in client code
- ⚠️ Never commit JWT secret to git

### Environment Variables

```bash
# .env.example
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
ENVIRONMENT=production

# .gitignore
.env
```

---

## Troubleshooting

### "Invalid authentication token"

1. Check token is not expired
2. Verify JWT secret matches Supabase dashboard
3. Ensure token is properly formatted (Bearer prefix)
4. Check environment is set correctly

### "Token expired"

- Tokens expire after a set time (default 1 hour)
- Client should refresh token before expiration
- Supabase client handles automatic refresh

### "Signature verification failed"

1. Verify `SUPABASE_JWT_SECRET` in `.env`
2. Check JWT secret matches Supabase dashboard
3. For development, set `ENVIRONMENT=development` to skip verification

### "Athlete not found"

- Ensure `auth_user_id` in query matches JWT `sub` field
- Verify athlete is linked to auth user in database:
  ```sql
  SELECT id, first_name, last_name, auth_user_id
  FROM athletes
  WHERE auth_user_id = 'uuid-here';
  ```

---

## Migration from API Key to JWT

### Phase 1: Add JWT Support (Backwards Compatible)

✅ Current implementation supports both:
- JWT tokens validated first
- API key as fallback

### Phase 2: Client Migration

Update iOS app to use Supabase Auth tokens:

```swift
// Old (API key)
request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")

// New (JWT token)
let session = try await supabase.auth.session
request.setValue("Bearer \(session.accessToken)", forHTTPHeaderField: "Authorization")
```

### Phase 3: Deprecate API Key (Optional)

Remove API key fallback from `api/main.py:get_current_user`:

```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    # Only JWT validation
    user_info = supabase_auth.validate_token(token)
    return user_info
```

---

## Testing Checklist

- [ ] JWT token generation script works
- [ ] Test JWT token validates in development
- [ ] Test JWT token validates in production (with signature verification)
- [ ] Test token expiration handling
- [ ] Test invalid token rejection
- [ ] Test API key fallback (if enabled)
- [ ] Test iOS app authentication flow
- [ ] Test token refresh in iOS app

---

## References

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [JWT.io - Token Debugger](https://jwt.io/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)