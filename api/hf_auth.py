"""
HuggingFace Space Authentication
Authentication middleware for HuggingFace Space API endpoints

CRITICAL RULES:
- Verify HF_TOKEN from environment
- Return error if token missing or invalid
- NO bypass - authentication is REQUIRED
"""

import os
import logging
from fastapi import Security, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

logger = logging.getLogger(__name__)

# Get HF_TOKEN from environment - REQUIRED for authentication
HF_TOKEN_ENV = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")

# Security scheme
security = HTTPBearer(auto_error=False)


async def verify_hf_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    authorization: Optional[str] = Header(None)
) -> bool:
    """
    Verify HuggingFace API token
    
    CRITICAL RULES:
    1. MUST check credentials from Bearer token OR Authorization header
    2. MUST compare with HF_TOKEN from environment
    3. MUST return 401 if token missing or invalid
    4. NO fake authentication - REAL token verification ONLY
    
    Args:
        credentials: HTTP Bearer token credentials
        authorization: Authorization header (fallback)
    
    Returns:
        bool: True if authenticated
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    
    # Get token from credentials or header
    provided_token = None
    
    if credentials:
        provided_token = credentials.credentials
    elif authorization:
        # Handle "Bearer TOKEN" format
        if authorization.startswith("Bearer "):
            provided_token = authorization[7:]
        else:
            provided_token = authorization
    
    # If no token provided, return 401
    if not provided_token:
        logger.warning("Authentication failed: No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": "Authentication required. Please provide HF_TOKEN in Authorization header.",
                "source": "hf_engine"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # If HF_TOKEN not configured in environment, return 401
    if not HF_TOKEN_ENV:
        logger.error("HF_TOKEN not configured in environment")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": "HF_TOKEN not configured on server. Please set HF_TOKEN environment variable.",
                "source": "hf_engine"
            }
        )
    
    # Verify token matches
    # CRITICAL: This is REAL token verification - NO bypass
    if provided_token != HF_TOKEN_ENV:
        logger.warning(f"Authentication failed: Invalid token provided (length: {len(provided_token)})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": "Invalid authentication token",
                "source": "hf_engine"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Token is valid
    logger.info("Authentication successful")
    return True


async def optional_hf_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    authorization: Optional[str] = Header(None)
) -> Optional[bool]:
    """
    Optional HF token verification (for endpoints that can work without auth)
    
    Returns:
        Optional[bool]: True if authenticated, None if no token provided
    """
    try:
        return await verify_hf_token(credentials, authorization)
    except HTTPException:
        # Return None if authentication fails (optional mode)
        return None
