"""
Generate a test JWT token for local development

This script creates a JWT token that mimics a Supabase Auth token
for testing purposes.
"""

import jwt
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import get_settings

settings = get_settings()


def generate_test_jwt(
    user_id: str,
    email: str,
    expiration_hours: int = 24
) -> str:
    """
    Generate a test JWT token

    Args:
        user_id: Supabase user UUID
        email: User email
        expiration_hours: Token expiration in hours (default: 24)

    Returns:
        JWT token string
    """
    # JWT secret (using service key as fallback)
    jwt_secret = settings.SUPABASE_JWT_SECRET or settings.SUPABASE_SERVICE_KEY

    # Token expiration
    exp = datetime.utcnow() + timedelta(hours=expiration_hours)
    iat = datetime.utcnow()

    # JWT payload (mimicking Supabase Auth token structure)
    payload = {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "exp": int(exp.timestamp()),
        "iat": int(iat.timestamp()),
        "iss": settings.SUPABASE_URL,  # Issuer
    }

    # Encode JWT
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")

    return token


if __name__ == "__main__":
    # Default test user (your actual auth user)
    test_user_id = "bab94363-5d47-4118-89a5-73ec3331e1d6"
    test_email = "jackrudelic@gmail.com"

    # Allow passing custom user_id and email as arguments
    if len(sys.argv) > 1:
        test_user_id = sys.argv[1]
    if len(sys.argv) > 2:
        test_email = sys.argv[2]

    # Generate token
    token = generate_test_jwt(test_user_id, test_email)

    print("=" * 80)
    print("TEST JWT TOKEN GENERATED")
    print("=" * 80)
    print(f"\nUser ID: {test_user_id}")
    print(f"Email: {test_email}")
    print(f"Expires: 24 hours")
    print(f"\nToken:\n{token}")
    print("\n" + "=" * 80)
    print("USAGE")
    print("=" * 80)
    print("\nTest with curl:")
    print(f'\ncurl -X GET "http://localhost:8000/enhanced/athlete/stats?auth_user_id={test_user_id}" \\')
    print(f'  -H "Authorization: Bearer {token}"')
    print("\n" + "=" * 80)