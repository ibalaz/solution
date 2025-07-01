import logging
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException

from .models import User

logger = logging.getLogger(__name__)


class DummyJSONClient:
    def __init__(self, base_url: str = "https://dummyjson.com"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    async def get_todos(self) -> List[Dict]:
        try:
            response = await self.client.get(f"{self.base_url}/todos")
            response.raise_for_status()
            data = response.json()
            return data.get("todos", [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch todos: {e}")
            raise HTTPException(status_code=503, detail="External service unavailable")
    
    async def get_todo_by_id(self, todo_id: int) -> Optional[Dict]:
        try:
            response = await self.client.get(f"{self.base_url}/todos/{todo_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch todo {todo_id}: {e}")
            raise HTTPException(status_code=503, detail="External service unavailable")
    
    async def get_users(self) -> List[User]:
        try:
            response = await self.client.get(f"{self.base_url}/users")
            response.raise_for_status()
            data = response.json()
            users_data = data.get("users", [])
            return [User(**user) for user in users_data]
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch users: {e}")
            raise HTTPException(status_code=503, detail="External service unavailable")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            response = await self.client.get(f"{self.base_url}/users/{user_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            user_data = response.json()
            return User(**user_data)
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch user {user_id}: {e}")
            raise HTTPException(status_code=503, detail="External service unavailable")
    
    async def authenticate(self, username: str, password: str) -> Optional[Dict]:
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 400:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Authentication failed: {e}")
            raise HTTPException(status_code=503, detail="Authentication service unavailable")


# Global client instance
dummy_client = DummyJSONClient()