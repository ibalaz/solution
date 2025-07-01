# TicketHub Project Specification

## Overview
Create a FastAPI middleware REST service that collects and exposes support tickets from external sources for AI agent processing.

## Requirements

### Technology Stack
- Python 3.11 with typing, async/await
- FastAPI 0.111 with automatic OpenAPI
- httpx 0.27 for external API calls
- pydantic 2.7 for validation
- pytest for testing

### External Data Source
- Tickets: https://dummyjson.com/todos
- Users: https://dummyjson.com/users

### Data Transformation
Transform DummyJSON todos to Ticket model:
- id: int (from todo id)
- title: string (from todo field)
- status: "closed" if completed == true, else "open"
- priority: calculate from id % 3 → low/medium/high
- assignee: username from userId lookup

### Required Endpoints
1. GET /tickets - paginated list (id, title, status, priority, description ≤ 100 chars)
2. GET /tickets/{id} - detailed ticket + full JSON from source
3. GET /tickets?status=<>&priority=<> - filtering
4. GET /tickets/search?q=... - search by title

### Nice-to-Have Features
- /stats - aggregated statistics
- JWT authentication using DummyJSON /auth/login
- Caching (Redis or in-memory TTL)
- Rate limiting
- Logging (INFO/WARNING/ERROR)
- Health-check endpoint for k8s/Compose

### Project Structure Requirements
- Clear structure: src/, tests/, ci/
- PEP-8 style compliance
- CI workflow (GitHub Actions)
- README.md with setup instructions
- Dockerfile + docker-compose.yml
- Makefile for run/lint/test/docker-build
- Feature-based commits

### Deliverables
1. Complete FastAPI application
2. Comprehensive test suite
3. Docker configuration
4. CI/CD pipeline
5. Documentation

## Implementation Notes
- Use async/await throughout
- Proper error handling
- Structured logging
- Comprehensive validation
- Rate limiting protection
- Health monitoring
- Production-ready configuration