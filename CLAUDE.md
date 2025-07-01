# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TicketHub is a FastAPI middleware REST service that collects and exposes support tickets from external sources (DummyJSON) for AI agent processing. It transforms todo items into structured tickets with filtering, pagination, search, authentication, and rate limiting.

## Technology Stack

- **Backend**: FastAPI 0.111 with Python 3.11
- **HTTP Client**: httpx 0.27 for external API calls
- **Validation**: Pydantic 2.7 for data models
- **Authentication**: JWT with python-jose and passlib
- **Testing**: pytest with asyncio support and coverage
- **Rate Limiting**: slowapi
- **Containerization**: Docker with multi-stage builds

## Common Development Commands

```bash
# Installation and setup
make install              # Install dependencies
make dev                 # Install dev dependencies

# Development
make run                 # Run development server with reload
make test                # Run test suite
make test-cov            # Run tests with coverage report
make lint                # Run flake8 and mypy
make format              # Format code with black and isort
make format-check        # Check formatting without changes

# Docker
make docker-build        # Build Docker image
make docker-run          # Run with Docker Compose (includes Redis)
make docker-stop         # Stop Docker services

# Cleanup
make clean               # Remove cache files and artifacts
```

## Project Architecture

### Directory Structure
```
src/tickethub/           # Main application package
├── main.py             # FastAPI app, routes, middleware
├── models.py           # Pydantic data models
├── service.py          # Business logic and data transformation
├── external_client.py  # DummyJSON API client
├── auth.py             # JWT authentication
└── cache.py            # In-memory caching (TTL-based)

tests/                  # Comprehensive test suite
├── conftest.py         # Test fixtures and mocks
├── test_*.py           # Test modules by component
```

### Key Components

- **FastAPI App** (`main.py`): Routes, middleware, rate limiting, error handling
- **Service Layer** (`service.py`): Data transformation, filtering, pagination, stats
- **External Client** (`external_client.py`): Async HTTP client for DummyJSON APIs
- **Models** (`models.py`): Pydantic models for validation and serialization
- **Authentication** (`auth.py`): JWT token management and user validation

### Data Flow
1. External APIs (DummyJSON todos/users) → `external_client.py`
2. Raw data transformation → `service.py` 
3. Business logic and filtering → `service.py`
4. HTTP endpoints and validation → `main.py`

## Testing Strategy

- **Unit Tests**: All components have isolated unit tests with mocks
- **API Tests**: Full endpoint testing with TestClient
- **Fixtures**: Centralized test data and mocking in `conftest.py`
- **Coverage**: Aim for >90% code coverage
- **Async Testing**: Uses pytest-asyncio for async/await code

Run tests: `make test` or `python -m pytest tests/ -v`

## External Dependencies

The application integrates with DummyJSON APIs:
- **Todos**: https://dummyjson.com/todos (source of ticket data)
- **Users**: https://dummyjson.com/users (for assignee information)
- **Auth**: https://dummyjson.com/auth/login (authentication service)

Data is transformed from todos to tickets with calculated priority and status mapping.

## Development Notes

- **Async/Await**: All I/O operations use async patterns
- **Error Handling**: Comprehensive HTTP exception handling with proper status codes
- **Rate Limiting**: Applied per-endpoint with reasonable limits
- **Caching**: In-memory TTL cache for user data to reduce API calls
- **Security**: JWT authentication, input validation, security headers
- **Logging**: Structured logging with INFO/WARNING/ERROR levels
- **Health Checks**: Available at `/health` for monitoring

## Code Quality Standards

- **Formatting**: Black (88 char line length)
- **Import Sorting**: isort
- **Linting**: flake8 with E203, W503 ignored for Black compatibility  
- **Type Checking**: mypy with ignore-missing-imports
- **Security**: bandit for security analysis
- **Dependencies**: safety for vulnerability scanning