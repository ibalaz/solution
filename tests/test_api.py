import pytest
from unittest.mock import patch

from src.tickethub.models import TicketStatus, TicketPriority


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "uptime" in data


def test_get_tickets_default(client):
    """Test getting tickets with default parameters."""
    response = client.get("/tickets")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    
    assert data["page"] == 1
    assert data["size"] == 20
    assert len(data["items"]) <= data["size"]


def test_get_tickets_with_pagination(client):
    """Test tickets pagination."""
    response = client.get("/tickets?page=1&size=2")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 1
    assert data["size"] == 2
    assert len(data["items"]) <= 2


def test_get_tickets_with_status_filter(client):
    """Test filtering tickets by status."""
    response = client.get("/tickets?status=open")
    
    assert response.status_code == 200
    data = response.json()
    
    for item in data["items"]:
        assert item["status"] == "open"


def test_get_tickets_with_priority_filter(client):
    """Test filtering tickets by priority."""
    response = client.get("/tickets?priority=high")
    
    assert response.status_code == 200
    data = response.json()
    
    for item in data["items"]:
        assert item["priority"] == "high"


def test_get_tickets_with_search(client):
    """Test searching tickets."""
    response = client.get("/tickets?q=Test")
    
    assert response.status_code == 200
    data = response.json()
    
    for item in data["items"]:
        assert "test" in item["title"].lower()


def test_search_tickets_endpoint(client):
    """Test dedicated search endpoint."""
    response = client.get("/tickets/search?q=Test")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    for item in data["items"]:
        assert "test" in item["title"].lower()


def test_search_tickets_missing_query(client):
    """Test search endpoint without query parameter."""
    response = client.get("/tickets/search")
    
    assert response.status_code == 422  # Validation error


def test_get_ticket_by_id(client):
    """Test getting specific ticket by ID."""
    response = client.get("/tickets/1")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == 1
    assert "title" in data
    assert "status" in data
    assert "priority" in data
    assert "assignee" in data
    assert "description" in data
    assert "source_data" in data


def test_get_ticket_by_id_not_found(client):
    """Test getting non-existent ticket."""
    with patch("src.tickethub.service.ticket_service.get_ticket_by_id", return_value=None):
        response = client.get("/tickets/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Ticket not found"


def test_get_stats(client):
    """Test getting ticket statistics."""
    response = client.get("/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    required_fields = [
        "total_tickets", "open_tickets", "closed_tickets",
        "low_priority", "medium_priority", "high_priority",
        "assignee_distribution"
    ]
    
    for field in required_fields:
        assert field in data
    
    assert isinstance(data["assignee_distribution"], dict)


def test_login_endpoint(client):
    """Test authentication endpoint."""
    response = client.post(
        "/auth/login",
        data={"username": "test_user", "password": "test_pass"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    with patch("src.tickethub.auth.authenticate_user", return_value=None):
        response = client.post(
            "/auth/login",
            data={"username": "invalid", "password": "invalid"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid credentials"


def test_pagination_validation(client):
    """Test pagination parameter validation."""
    # Invalid page number
    response = client.get("/tickets?page=0")
    assert response.status_code == 422
    
    # Invalid page size
    response = client.get("/tickets?size=0")
    assert response.status_code == 422
    
    # Page size too large
    response = client.get("/tickets?size=1000")
    assert response.status_code == 422


def test_openapi_docs(client):
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_data = response.json()
    assert openapi_data["info"]["title"] == "TicketHub API"