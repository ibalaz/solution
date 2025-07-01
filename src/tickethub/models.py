from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(BaseModel):
    id: int
    username: str
    email: str
    firstName: str
    lastName: str
    gender: str
    image: str
    phone: str
    birthDate: str
    age: int


class TicketBase(BaseModel):
    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    assignee: str
    description: str = Field(..., max_length=100)


class Ticket(TicketBase):
    pass


class TicketDetail(TicketBase):
    source_data: Dict[str, Any] = Field(..., description="Full JSON from source")


class PaginatedResponse(BaseModel):
    items: List[Ticket]
    total: int
    page: int
    size: int
    pages: int


class TicketStats(BaseModel):
    total_tickets: int
    open_tickets: int
    closed_tickets: int
    low_priority: int
    medium_priority: int
    high_priority: int
    assignee_distribution: Dict[str, int]


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float