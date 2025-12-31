"""JWT verification utilities for Better Auth tokens."""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt as pyjwt
from jwt import PyJWKClient
from jose import jwt as jose_jwt

load_dotenv()

# Security scheme for extracting Bearer token
security = HTTPBearer()

# Cache for the public key
_cached_public_key: Optional[Any] = None


def get_public_key_from_db():
    """Fetch the Ed25519 public key from Better Auth's JWKS table."""
    global _cached_public_key

    if _cached_public_key is not None:
        return _cached_public_key

    from database import engine
    from sqlmodel import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT \"publicKey\" FROM jwks LIMIT 1"))
        row = result.fetchone()
        if row:
            public_key_json = json.loads(row[0])
            print(f"Loaded public key from DB: {public_key_json}")
            _cached_public_key = public_key_json
            return public_key_json

    raise ValueError("No JWKS found in database")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token signed with Ed25519 (EdDSA) and extract payload.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    # First, decode without verification to see the token structure
    try:
        unverified_header = jose_jwt.get_unverified_header(token)
        unverified = jose_jwt.get_unverified_claims(token)
        print(f"Token header: {unverified_header}")
        print(f"Token claims (unverified): {unverified}")
    except Exception as e:
        print(f"Failed to decode token structure: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        ) from e

    try:
        # Get the public key from Better Auth's JWKS table
        public_key_jwk = get_public_key_from_db()

        # Convert JWK to PEM format for PyJWT
        from jwt.algorithms import OKPAlgorithm

        # Create the key from JWK
        key = OKPAlgorithm.from_jwk(public_key_jwk)

        # Verify and decode the token using EdDSA
        payload = pyjwt.decode(
            token,
            key,
            algorithms=["EdDSA"],
            options={"verify_aud": False}
        )
        print("Token verification successful")
        return payload

    except pyjwt.ExpiredSignatureError:
        print("Token has expired")
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except pyjwt.InvalidTokenError as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        ) from e
    except Exception as e:
        print(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        ) from e


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and verify the current user from JWT.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User dict with id and email from token claims

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    token = credentials.credentials
    payload = verify_token(token)

    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: missing user ID"
        )

    return {
        "id": user_id,
        "email": email
    }
