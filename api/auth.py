"""
Authentication and Security for API Endpoints
"""

from fastapi import HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import config

security = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token"""
    # If no tokens configured, allow access
    if not config.API_TOKENS:
        return None

    # If tokens configured, require authentication
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    if credentials.credentials not in config.API_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        )

    return credentials.credentials


async def verify_ip(request: Request):
    """Verify IP whitelist"""
    if not config.ALLOWED_IPS:
        # No IP restriction
        return True

    client_ip = request.client.host
    if client_ip not in config.ALLOWED_IPS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IP not whitelisted")

    return True
