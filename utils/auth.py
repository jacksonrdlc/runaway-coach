"""
Supabase JWT Authentication

Validates JWT tokens from Supabase Auth and extracts user information.
"""

import jwt
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from datetime import datetime

from utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SupabaseAuth:
    """Supabase JWT authentication and validation"""

    def __init__(self):
        # Use JWT secret if available, otherwise fall back to service key
        self.jwt_secret = settings.SUPABASE_JWT_SECRET or settings.SUPABASE_SERVICE_KEY
        self.environment = settings.ENVIRONMENT

        # In production, always verify signatures
        # In development, can skip verification for easier testing
        self.verify_signature_default = self.environment == "production"

        logger.info(f"SupabaseAuth initialized for {self.environment} environment")
        if not settings.SUPABASE_JWT_SECRET and self.environment == "production":
            logger.warning("SUPABASE_JWT_SECRET not set in production - using service key as fallback")

    def decode_token(self, token: str, verify_signature: Optional[bool] = None) -> Dict[str, Any]:
        """
        Decode and validate Supabase JWT token

        Args:
            token: JWT token string
            verify_signature: Whether to verify the signature (defaults based on environment)

        Returns:
            Decoded token payload with user info

        Raises:
            HTTPException: If token is invalid or expired
        """
        # Use default verification based on environment if not specified
        if verify_signature is None:
            verify_signature = self.verify_signature_default

        try:
            # Decode JWT token
            if verify_signature:
                # Verify signature with JWT secret
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=["HS256"],
                    options={
                        "verify_exp": True,
                        "verify_aud": False  # Don't verify audience
                    }
                )
            else:
                # Skip signature verification (dev only)
                payload = jwt.decode(
                    token,
                    options={
                        "verify_signature": False,
                        "verify_exp": True
                    },
                    algorithms=["HS256"]
                )

            # Validate required fields
            if "sub" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )

            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )

    def extract_user_info(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user information from decoded JWT payload

        Args:
            payload: Decoded JWT payload

        Returns:
            Dictionary with user information
        """
        return {
            "user_id": payload.get("sub"),  # Supabase user UUID
            "auth_user_id": payload.get("sub"),  # Same as user_id
            "email": payload.get("email"),
            "role": payload.get("role"),
            "aud": payload.get("aud"),  # Audience (usually "authenticated")
            "exp": payload.get("exp"),  # Expiration timestamp
            "iat": payload.get("iat"),  # Issued at timestamp
        }

    def validate_token(self, token: str, verify_signature: Optional[bool] = None) -> Dict[str, Any]:
        """
        Validate token and return user info (convenience method)

        Args:
            token: JWT token string
            verify_signature: Whether to verify signature (defaults based on environment)

        Returns:
            Dictionary with user information
        """
        payload = self.decode_token(token, verify_signature=verify_signature)
        return self.extract_user_info(payload)


# Singleton instance
_auth_instance: Optional[SupabaseAuth] = None


def get_supabase_auth() -> SupabaseAuth:
    """Get SupabaseAuth singleton instance"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = SupabaseAuth()
    return _auth_instance