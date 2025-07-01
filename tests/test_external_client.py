import pytest
from unittest.mock import AsyncMock, patch
import httpx
from fastapi import HTTPException

from src.tickethub.external_client import DummyJSONClient
from src.tickethub.models import User


@pytest.fixture
def client():
    """Create a DummyJSONClient instance for testing."""
    return DummyJSONClient()


@pytest.mark.asyncio
async def test_get_todos_success(client):
    """Test successful todos retrieval."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "todos": [
            {"id": 1, "todo": "Test todo", "completed": False, "userId": 1}
        ]
    }
    mock_response.raise_for_status.return_value = None
    
    with patch.object(client.client, 'get', return_value=mock_response):
        todos = await client.get_todos()
        
        assert len(todos) == 1
        assert todos[0]["id"] == 1
        assert todos[0]["todo"] == "Test todo"


@pytest.mark.asyncio
async def test_get_todos_http_error(client):
    """Test todos retrieval with HTTP error."""
    with patch.object(client.client, 'get', side_effect=httpx.HTTPError("Network error")):
        with pytest.raises(HTTPException) as exc_info:
            await client.get_todos()
        
        assert exc_info.value.status_code == 503
        assert "External service unavailable" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_todo_by_id_success(client):
    """Test successful single todo retrieval."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "id": 1, "todo": "Test todo", "completed": False, "userId": 1
    }
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    
    with patch.object(client.client, 'get', return_value=mock_response):
        todo = await client.get_todo_by_id(1)
        
        assert todo is not None
        assert todo["id"] == 1


@pytest.mark.asyncio
async def test_get_todo_by_id_not_found(client):
    """Test todo retrieval when not found."""
    mock_response = AsyncMock()
    mock_response.status_code = 404
    
    with patch.object(client.client, 'get', return_value=mock_response):
        todo = await client.get_todo_by_id(999)
        
        assert todo is None


@pytest.mark.asyncio
async def test_get_users_success(client):
    """Test successful users retrieval."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "users": [
            {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "gender": "male",
                "image": "https://example.com/john.jpg",
                "phone": "123-456-7890",
                "birthDate": "1990-01-01",
                "age": 33
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    
    with patch.object(client.client, 'get', return_value=mock_response):
        users = await client.get_users()
        
        assert len(users) == 1
        assert isinstance(users[0], User)
        assert users[0].username == "john_doe"


@pytest.mark.asyncio
async def test_get_user_by_id_success(client):
    """Test successful single user retrieval."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "gender": "male",
        "image": "https://example.com/john.jpg",
        "phone": "123-456-7890",
        "birthDate": "1990-01-01",
        "age": 33
    }
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    
    with patch.object(client.client, 'get', return_value=mock_response):
        user = await client.get_user_by_id(1)
        
        assert user is not None
        assert isinstance(user, User)
        assert user.username == "john_doe"


@pytest.mark.asyncio
async def test_authenticate_success(client):
    """Test successful authentication."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "token": "test_token",
        "username": "test_user"
    }
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    
    with patch.object(client.client, 'post', return_value=mock_response):
        auth_data = await client.authenticate("test_user", "test_pass")
        
        assert auth_data is not None
        assert auth_data["token"] == "test_token"


@pytest.mark.asyncio
async def test_authenticate_invalid_credentials(client):
    """Test authentication with invalid credentials."""
    mock_response = AsyncMock()
    mock_response.status_code = 400
    
    with patch.object(client.client, 'post', return_value=mock_response):
        auth_data = await client.authenticate("invalid", "invalid")
        
        assert auth_data is None


@pytest.mark.asyncio
async def test_client_close(client):
    """Test client cleanup."""
    with patch.object(client.client, 'aclose') as mock_close:
        await client.close()
        mock_close.assert_called_once()