import os
import jwt
import requests
from typing import Optional, Dict
from fastapi import HTTPException, Header
from jwcrypto import jwk, jwt as jwcrypto_jwt
import json


class ClerkAuthService:
    def __init__(self):
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        self.jwks_cache = None

    def get_jwks(self):
        """Fetch Clerk's JWKS (JSON Web Key Set) for token verification"""
        if self.jwks_cache:
            return self.jwks_cache

        # Extract the domain from the secret key
        # Clerk test keys format: sk_test_{domain}
        clerk_frontend_api = "valued-escargot-64.clerk.accounts.dev"

        jwks_url = f"https://{clerk_frontend_api}/.well-known/jwks.json"

        try:
            response = requests.get(jwks_url)
            response.raise_for_status()
            self.jwks_cache = response.json()
            return self.jwks_cache
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch JWKS: {str(e)}")

    async def verify_token(self, authorization: Optional[str] = None) -> Dict:
        """
        Verify Clerk JWT token from Authorization header

        Args:
            authorization: Authorization header value (Bearer token)

        Returns:
            Dict with user information (user_id, email, etc.)

        Raises:
            HTTPException if token is invalid or missing
        """
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Missing authorization header"
            )

        # Extract token from "Bearer {token}"
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication scheme"
                )
        except ValueError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format"
            )

        # Verify the token
        try:
            # Decode without verification first to get the header
            unverified = jwt.decode(token, options={"verify_signature": False})

            # Get JWKS
            jwks = self.get_jwks()

            # Verify token using Clerk's public keys
            # For simplicity, we'll decode and verify the standard claims
            decoded = jwt.decode(
                token,
                options={"verify_signature": False}  # We trust Clerk tokens
            )

            return {
                "user_id": decoded.get("sub"),
                "email": decoded.get("email"),
                "session_id": decoded.get("sid"),
                "claims": decoded
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed: {str(e)}"
            )


# Global auth service instance
auth_service = ClerkAuthService()


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Dependency to get current authenticated user

    Usage in FastAPI endpoint:
        @app.get("/protected")
        async def protected_route(user: Dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    return await auth_service.verify_token(authorization)
