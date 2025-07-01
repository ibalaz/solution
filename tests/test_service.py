import pytest
from unittest.mock import AsyncMock, MagicMock

from src.tickethub.service import TicketService
from src.tickethub.models import TicketPriority, TicketStatus


@pytest.fixture
def ticket_service():
    """Create a fresh TicketService instance for testing."""
    return TicketService()


@pytest.mark.asyncio
async def test_calculate_priority():
    """Test priority calculation based on ID modulo."""
    service = TicketService()
    
    assert service._calculate_priority(1) == TicketPriority.MEDIUM  # 1 % 3 = 1
    assert service._calculate_priority(2) == TicketPriority.HIGH    # 2 % 3 = 2
    assert service._calculate_priority(3) == TicketPriority.LOW     # 3 % 3 = 0


def test_truncate_description():
    """Test description truncation."""
    service = TicketService()
    
    short_text = "Short description"
    long_text = "This is a very long description that exceeds the maximum allowed length and should be truncated"
    
    assert service._truncate_description(short_text) == short_text
    truncated = service._truncate_description(long_text, 50)
    assert len(truncated) == 50
    assert truncated.endswith("...")


@pytest.mark.asyncio
async def test_transform_todo_to_ticket(ticket_service, mock_dummy_client):
    """Test transformation from todo to ticket."""
    todo_data = {
        "id": 1,
        "todo": "Test todo item",
        "completed": False,
        "userId": 1
    }
    
    ticket = await ticket_service._transform_todo_to_ticket(todo_data)
    
    assert ticket.id == 1
    assert ticket.title == "Test todo item"
    assert ticket.status == TicketStatus.OPEN
    assert ticket.priority == TicketPriority.MEDIUM  # 1 % 3 = 1
    assert ticket.assignee == "john_doe"
    assert ticket.description == "Test todo item"


@pytest.mark.asyncio
async def test_transform_completed_todo_to_ticket(ticket_service, mock_dummy_client):
    """Test transformation of completed todo to ticket."""
    todo_data = {
        "id": 2,
        "todo": "Completed todo",
        "completed": True,
        "userId": 2
    }
    
    ticket = await ticket_service._transform_todo_to_ticket(todo_data)
    
    assert ticket.status == TicketStatus.CLOSED
    assert ticket.assignee == "jane_smith"


@pytest.mark.asyncio
async def test_get_tickets_with_filters(ticket_service, mock_dummy_client):
    """Test getting tickets with various filters."""
    # Test status filter
    open_tickets = await ticket_service.get_tickets(status=TicketStatus.OPEN)
    assert len(open_tickets) == 2  # todos 1 and 3 are not completed
    
    closed_tickets = await ticket_service.get_tickets(status=TicketStatus.CLOSED)
    assert len(closed_tickets) == 1  # todo 2 is completed


@pytest.mark.asyncio
async def test_get_tickets_with_search(ticket_service, mock_dummy_client):
    """Test getting tickets with search query."""
    tickets = await ticket_service.get_tickets(search="Test todo 1")
    assert len(tickets) == 1
    assert tickets[0].title == "Test todo 1"
    
    # Case insensitive search
    tickets = await ticket_service.get_tickets(search="test todo 2")
    assert len(tickets) == 1
    assert tickets[0].title == "Test todo 2"


@pytest.mark.asyncio
async def test_get_tickets_pagination(ticket_service, mock_dummy_client):
    """Test ticket pagination."""
    # First page
    tickets = await ticket_service.get_tickets(skip=0, limit=2)
    assert len(tickets) == 2
    
    # Second page
    tickets = await ticket_service.get_tickets(skip=2, limit=2)
    assert len(tickets) == 1  # Only one ticket left


@pytest.mark.asyncio
async def test_get_ticket_by_id(ticket_service, mock_dummy_client):
    """Test getting ticket by ID."""
    ticket = await ticket_service.get_ticket_by_id(1)
    
    assert ticket is not None
    assert ticket.id == 1
    assert ticket.title == "Test todo 1"
    assert ticket.source_data["id"] == 1


@pytest.mark.asyncio
async def test_get_ticket_by_id_not_found(ticket_service, mock_dummy_client):
    """Test getting non-existent ticket."""
    ticket = await ticket_service.get_ticket_by_id(999)
    assert ticket is None


@pytest.mark.asyncio
async def test_get_total_tickets_count(ticket_service, mock_dummy_client):
    """Test getting total tickets count."""
    total = await ticket_service.get_total_tickets_count()
    assert total == 3
    
    # With filters
    open_count = await ticket_service.get_total_tickets_count(status=TicketStatus.OPEN)
    assert open_count == 2


@pytest.mark.asyncio
async def test_get_ticket_stats(ticket_service, mock_dummy_client):
    """Test getting ticket statistics."""
    stats = await ticket_service.get_ticket_stats()
    
    assert stats.total_tickets == 3
    assert stats.open_tickets == 2
    assert stats.closed_tickets == 1
    assert stats.low_priority == 1  # ticket 3 (3 % 3 = 0)
    assert stats.medium_priority == 1  # ticket 1 (1 % 3 = 1)
    assert stats.high_priority == 1  # ticket 2 (2 % 3 = 2)
    assert "john_doe" in stats.assignee_distribution
    assert "jane_smith" in stats.assignee_distribution