import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from src.tickethub.main import app
from src.tickethub.external_client import dummy_client
from src.tickethub.service import ticket_service


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_dummy_client():
    """Mock the external DummyJSON client."""
    mock_client = AsyncMock()
    
    # Mock todos data
    mock_todos = [
        {"id": 1, "todo": "Test todo 1", "completed": False, "userId": 1},
        {"id": 2, "todo": "Test todo 2", "completed": True, "userId": 2},
        {"id": 3, "todo": "Test todo 3", "completed": False, "userId": 1},
    ]
    
    # Mock users data
    mock_users = [
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
        },
        {
            "id": 2,
            "username": "jane_smith",
            "email": "jane@example.com",
            "firstName": "Jane",
            "lastName": "Smith",
            "gender": "female",
            "image": "https://example.com/jane.jpg",
            "phone": "098-765-4321",
            "birthDate": "1985-05-15",
            "age": 38
        }
    ]
    
    mock_client.get_todos.return_value = mock_todos
    mock_client.get_todo_by_id.side_effect = lambda id: next(
        (todo for todo in mock_todos if todo["id"] == id), None
    )
    mock_client.get_users.return_value = [
        MagicMock(**user) for user in mock_users
    ]
    mock_client.get_user_by_id.side_effect = lambda id: next(
        (MagicMock(**user) for user in mock_users if user["id"] == id), None
    )
    mock_client.authenticate.return_value = {"token": "test_token", "username": "test_user"}
    
    return mock_client


@pytest.fixture(autouse=True)
def mock_external_client(monkeypatch, mock_dummy_client):
    """Automatically mock the external client for all tests."""
    monkeypatch.setattr("src.tickethub.external_client.dummy_client", mock_dummy_client)
    monkeypatch.setattr("src.tickethub.service.dummy_client", mock_dummy_client)
    
    # Reset the users cache
    ticket_service._users_cache = None