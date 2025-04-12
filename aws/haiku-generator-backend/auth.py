import json
import requests
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from pathlib import Path
from typing import Dict, Any

load_dotenv()


COGNITO_REGION = os.getenv("COGNITO_REGION")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
JWT_ALGORITHM = "RS256"


class CognitoJWTVerifier:
    def __init__(self):
        self._jwks = None
        self._jwks_url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        self._jwks_cache_file = Path(".jwks_cache.json")
        self._load_cached_jwks()

    def _load_cached_jwks(self):
        """Load JWKS from cache file if it exists"""
        if self._jwks_cache_file.exists():
            try:
                with open(self._jwks_cache_file, 'r') as f:
                    self._jwks = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cached JWKS: {str(e)}")

    def _save_jwks_to_cache(self, jwks: Dict[str, Any]):
        """Save JWKS to cache file"""
        try:
            with open(self._jwks_cache_file, 'w') as f:
                json.dump(jwks, f)
        except Exception as e:
            print(f"Warning: Failed to save JWKS cache: {str(e)}")

    async def verify_token(self, token: str) -> dict:
        """
        Verify JWT token.
        """
        try:
            # Get the kid from the token header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header["kid"]

            # Get JWKS if not cached
            if not self._jwks:
                self._jwks = await self._get_jwks()
                self._save_jwks_to_cache(self._jwks)

            # Find the matching key
            key = next((k for k in self._jwks["keys"] if k["kid"] == kid), None)
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Decode the token
            claims = jwt.decode(
                token,
                key,
                algorithms=[JWT_ALGORITHM],
                audience=COGNITO_CLIENT_ID,
                options={"verify_exp": True}
            )
            return claims

        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    async def _get_jwks(self) -> dict:
        """Get JWKS from Cognito"""
        try:
            response = requests.get(self._jwks_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get JWKS: {str(e)}")

verifier = CognitoJWTVerifier()

async def get_user_id(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> str:
    """
    Validate Cognito JWT token and return the user_id
    """
    try:
        token = credentials.credentials
        claims = await verifier.verify_token(token)
        user_id = claims.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user_id
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")