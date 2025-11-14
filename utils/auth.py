"""
Authentication and Authorization System
Implements JWT-based authentication for production deployments
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import logging
from functools import wraps

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("PyJWT not installed. Authentication disabled. Install with: pip install PyJWT")

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'


class AuthManager:
    """
    Authentication manager for API endpoints and dashboard access
    Supports JWT tokens and basic API key authentication
    """

    def __init__(self):
        self.users_db: Dict[str, str] = {}  # username -> hashed_password
        self.api_keys_db: Dict[str, Dict[str, Any]] = {}  # api_key -> metadata
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from environment variables"""
        # Load default admin user
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD')

        if admin_pass:
            self.users_db[admin_user] = self._hash_password(admin_pass)
            logger.info(f"Loaded admin user: {admin_user}")

        # Load API keys from environment
        api_keys_str = os.getenv('API_KEYS', '')
        if api_keys_str:
            for key in api_keys_str.split(','):
                key = key.strip()
                if key:
                    self.api_keys_db[key] = {
                        'created_at': datetime.utcnow(),
                        'name': 'env_key',
                        'active': True
                    }
            logger.info(f"Loaded {len(self.api_keys_db)} API keys")

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, username: str, password: str) -> bool:
        """
        Verify username and password

        Args:
            username: Username
            password: Plain text password

        Returns:
            True if valid, False otherwise
        """
        if username not in self.users_db:
            return False

        hashed = self._hash_password(password)
        return secrets.compare_digest(self.users_db[username], hashed)

    def create_access_token(
        self,
        username: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token

        Args:
            username: Username
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        if not JWT_AVAILABLE:
            raise RuntimeError("PyJWT not installed")

        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta
        payload = {
            'sub': username,
            'exp': expire,
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify JWT token and extract username

        Args:
            token: JWT token string

        Returns:
            Username if valid, None otherwise
        """
        if not JWT_AVAILABLE:
            return None

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get('sub')
            return username
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def verify_api_key(self, api_key: str) -> bool:
        """
        Verify API key

        Args:
            api_key: API key string

        Returns:
            True if valid and active, False otherwise
        """
        if api_key not in self.api_keys_db:
            return False

        key_data = self.api_keys_db[api_key]
        return key_data.get('active', False)

    def create_api_key(self, name: str) -> str:
        """
        Create new API key

        Args:
            name: Descriptive name for the key

        Returns:
            Generated API key
        """
        api_key = secrets.token_urlsafe(32)
        self.api_keys_db[api_key] = {
            'created_at': datetime.utcnow(),
            'name': name,
            'active': True,
            'usage_count': 0
        }
        logger.info(f"Created API key: {name}")
        return api_key

    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke API key

        Args:
            api_key: API key to revoke

        Returns:
            True if revoked, False if not found
        """
        if api_key in self.api_keys_db:
            self.api_keys_db[api_key]['active'] = False
            logger.info(f"Revoked API key: {self.api_keys_db[api_key]['name']}")
            return True
        return False

    def track_usage(self, api_key: str):
        """Track API key usage"""
        if api_key in self.api_keys_db:
            self.api_keys_db[api_key]['usage_count'] = \
                self.api_keys_db[api_key].get('usage_count', 0) + 1


# Global auth manager instance
auth_manager = AuthManager()


# ==================== DECORATORS ====================


def require_auth(func):
    """
    Decorator to require authentication for endpoints
    Checks for JWT token in Authorization header or API key in X-API-Key header
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not ENABLE_AUTH:
            # Authentication disabled, allow all requests
            return await func(*args, **kwargs)

        # Try to get token from request
        # This is a placeholder - actual implementation depends on framework (FastAPI, Flask, etc.)
        # For FastAPI:
        # from fastapi import Header, HTTPException
        # authorization: Optional[str] = Header(None)
        # api_key: Optional[str] = Header(None, alias="X-API-Key")

        # For now, this is a template
        raise NotImplementedError("Integrate with your web framework")

    return wrapper


def require_api_key(func):
    """Decorator to require API key authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not ENABLE_AUTH:
            return await func(*args, **kwargs)

        # Template for API key verification
        raise NotImplementedError("Integrate with your web framework")

    return wrapper


# ==================== HELPER FUNCTIONS ====================


def authenticate_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate user and return JWT token

    Args:
        username: Username
        password: Password

    Returns:
        JWT token if successful, None otherwise
    """
    if not ENABLE_AUTH:
        logger.warning("Authentication disabled")
        return None

    if auth_manager.verify_password(username, password):
        return auth_manager.create_access_token(username)

    return None


def verify_request_auth(
    authorization: Optional[str] = None,
    api_key: Optional[str] = None
) -> bool:
    """
    Verify request authentication

    Args:
        authorization: Authorization header (Bearer token)
        api_key: X-API-Key header

    Returns:
        True if authenticated, False otherwise
    """
    if not ENABLE_AUTH:
        return True

    # Check API key first
    if api_key and auth_manager.verify_api_key(api_key):
        auth_manager.track_usage(api_key)
        return True

    # Check JWT token
    if authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ')[1]
        username = auth_manager.verify_token(token)
        if username:
            return True

    return False
