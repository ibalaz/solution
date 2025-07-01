import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from .external_client import dummy_client
from .models import AuthResponse

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "a8f5f167f44f4964e6c998dee827110c284dfb3ea0a7bd5dc1e9dfa1e2f6dc9c3b2a8f9c7d4e1b2f8a3c9e6d4b7f2a1e8c5d3b9f7e2a4c8d6b1f5a9e3c7d2b8f4e1a6c9d5b3f7e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    return payload


async def authenticate_user(username: str, password: str) -> Optional[AuthResponse]:
    try:
        auth_data = await dummy_client.authenticate(username, password)
        if not auth_data:
            return None
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # Pass all data from external JWT token to our JWT token
        token_data = auth_data.copy()
        token_data["sub"] = username  # Ensure 'sub' field for JWT standard
        
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )
        
        return AuthResponse(access_token=access_token, token_type="bearer")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None