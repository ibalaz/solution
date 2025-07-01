import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .auth import authenticate_user
from .external_client import dummy_client
from .models import (
    AuthResponse, HealthCheck, PaginatedResponse, TicketDetail,
    TicketPriority, TicketStats, TicketStatus
)
from .service import ticket_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Application startup time
app_start_time = time.time()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TicketHub service...")
    yield
    logger.info("Shutting down TicketHub service...")
    await dummy_client.close()


app = FastAPI(
    title="TicketHub API",
    description="A FastAPI middleware REST service that collects and exposes support tickets from external sources for AI agent processing.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_pages(total: int, size: int) -> int:
    return (total + size - 1) // size


@app.post("/auth/login", response_model=AuthResponse)
@limiter.limit("5/minute")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Authenticate user and return JWT token."""
    auth_response = await authenticate_user(username, password)
    if not auth_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return auth_response


@app.get("/health", response_model=HealthCheck)
@limiter.limit("30/minute")
async def health_check(request:Request):
    """Health check endpoint for monitoring and orchestration."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=time.time() - app_start_time
    )


@app.get("/tickets", response_model=PaginatedResponse)
@limiter.limit("100/minute")
async def get_tickets(
    request:Request,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    ticket_status: Optional[TicketStatus] = Query(None, description="Filter by ticket status", enum=[ticket_status.value for ticket_status in TicketStatus]),
    priority: Optional[TicketPriority] = Query(None, description="Filter by ticket priority", enum=[priority.value for priority in TicketPriority]),
    title: Optional[str] = Query(None, description="Search by title"),
):
    """Get a paginated list of tickets with optional filtering and search."""
    try:
        skip = (page - 1) * size
        
        tickets = await ticket_service.get_tickets(
            skip=skip,
            limit=size,
            status=ticket_status,
            priority=priority,
            search=title
        )
        
        total = await ticket_service.get_total_tickets_count(
            status=ticket_status,
            priority=priority,
            search=title
        )
        
        pages = calculate_pages(total, size)
        
        return PaginatedResponse(
            items=tickets,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/tickets/search", response_model=PaginatedResponse)
@limiter.limit("50/minute")
async def search_tickets(
    request:Request,
    title: str = Query(..., description="Search query for ticket titles"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
):
    """Search tickets by title."""
    try:
        skip = (page - 1) * size
        
        tickets = await ticket_service.get_tickets(
            skip=skip,
            limit=size,
            search=title
        )
        
        total = await ticket_service.get_total_tickets_count(search=title)
        pages = calculate_pages(total, size)
        
        return PaginatedResponse(
            items=tickets,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        logger.error(f"Error searching tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/tickets/{ticket_id}", response_model=TicketDetail)
@limiter.limit("200/minute")
async def get_ticket_by_id(request:Request, ticket_id: int):
    """Get detailed ticket information including source data."""
    try:
        ticket = await ticket_service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/stats", response_model=TicketStats)
@limiter.limit("20/minute")
async def get_ticket_stats(request:Request):
    """Get aggregated ticket statistics."""
    try:
        return await ticket_service.get_ticket_stats()
    except Exception as e:
        logger.error(f"Error fetching ticket stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.tickethub.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )