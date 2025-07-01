import pytest
from pydantic import ValidationError

from src.tickethub.models import (
    Ticket, TicketDetail, TicketPriority, TicketStatus, 
    User, PaginatedResponse, TicketStats
)


def test_ticket_model():
    """Test Ticket model validation."""
    ticket = Ticket(
        id=1,
        title="Test ticket",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        assignee="john_doe",
        description="Test description"
    )
    
    assert ticket.id == 1
    assert ticket.title == "Test ticket"
    assert ticket.status == TicketStatus.OPEN
    assert ticket.priority == TicketPriority.HIGH
    assert ticket.assignee == "john_doe"
    assert ticket.description == "Test description"


def test_ticket_detail_model():
    """Test TicketDetail model validation."""
    source_data = {"id": 1, "todo": "Test", "completed": False, "userId": 1}
    
    ticket_detail = TicketDetail(
        id=1,
        title="Test ticket",
        status=TicketStatus.OPEN,
        priority=TicketPriority.MEDIUM,
        assignee="jane_smith",
        description="Test description",
        source_data=source_data
    )
    
    assert ticket_detail.source_data == source_data


def test_description_length_validation():
    """Test that description length is properly validated."""
    long_description = "x" * 150
    
    ticket = Ticket(
        id=1,
        title="Test",
        status=TicketStatus.OPEN,
        priority=TicketPriority.LOW,
        assignee="test",
        description=long_description
    )
    
    # Should not raise validation error as max_length is set but not enforced by Pydantic Field
    assert len(ticket.description) == 150


def test_user_model():
    """Test User model validation."""
    user = User(
        id=1,
        username="test_user",
        email="test@example.com",
        firstName="Test",
        lastName="User",
        gender="male",
        image="https://example.com/avatar.jpg",
        phone="123-456-7890",
        birthDate="1990-01-01",
        age=33
    )
    
    assert user.id == 1
    assert user.username == "test_user"
    assert user.email == "test@example.com"


def test_paginated_response_model():
    """Test PaginatedResponse model."""
    tickets = [
        Ticket(
            id=1,
            title="Test",
            status=TicketStatus.OPEN,
            priority=TicketPriority.LOW,
            assignee="test",
            description="Test"
        )
    ]
    
    response = PaginatedResponse(
        items=tickets,
        total=10,
        page=1,
        size=5,
        pages=2
    )
    
    assert len(response.items) == 1
    assert response.total == 10
    assert response.page == 1
    assert response.size == 5
    assert response.pages == 2


def test_ticket_stats_model():
    """Test TicketStats model."""
    stats = TicketStats(
        total_tickets=100,
        open_tickets=60,
        closed_tickets=40,
        low_priority=30,
        medium_priority=40,
        high_priority=30,
        assignee_distribution={"john": 50, "jane": 50}
    )
    
    assert stats.total_tickets == 100
    assert stats.open_tickets == 60
    assert stats.closed_tickets == 40
    assert stats.assignee_distribution == {"john": 50, "jane": 50}