# TicketHub API

A FastAPI middleware REST service that collects and exposes support tickets from external sources for AI agent processing.

## Features

- 🎯 **RESTful API** - Clean, well-documented endpoints
- 🔍 **Advanced Filtering** - Filter by status, priority, and search by title  
- 📄 **Pagination** - Efficient handling of large datasets
- 🔐 **JWT Authentication** - Secure access control
- ⚡ **Rate Limiting** - Protection against abuse
- 📊 **Statistics** - Aggregated ticket metrics
- 🐳 **Docker Ready** - Containerized deployment
- ✅ **Comprehensive Tests** - High test coverage
- 📝 **OpenAPI Documentation** - Auto-generated API docs

## Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd tickethub
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   make run
   # or
   uvicorn src.tickethub.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and run with Docker Compose
make docker-run
# or
docker-compose up --build

# Or build and run manually
make docker-build
docker run -p 8000:8000 tickethub:latest
```

## API Endpoints

### Core Endpoints

| Method | Endpoint                    | Description |
|--------|-----------------------------|-------------|
| GET | `/tickets`                  | Get paginated tickets with filtering |
| GET | `/tickets/{id}`             | Get detailed ticket with source data |
| GET | `/tickets/search?title=...` | Search tickets by title |
| GET | `/stats`                    | Get aggregated statistics |
| GET | `/health`                   | Health check endpoint |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Authenticate and get JWT token |

### Query Parameters

**GET /tickets**
- `page` (int): Page number (default: 1)
- `size` (int): Page size (default: 20, max: 100)
- `status` (string): Filter by status (`open`, `closed`)
- `priority` (string): Filter by priority (`low`, `medium`, `high`)
- `title` (string): Search query for title

**Example Requests:**
```bash
# Get all tickets
curl http://localhost:8000/tickets

# Get open tickets with high priority
curl "http://localhost:8000/tickets?status=open&priority=high"

# Search tickets
curl "http://localhost:8000/tickets/search?title=bug"

# Get ticket details
curl http://localhost:8000/tickets/1

# Get statistics
curl http://localhost:8000/stats

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=emilys&password=emilyspass"
```

## Data Model

### Ticket
```json
{
  "id": 1,
  "title": "Fix critical bug in authentication",
  "status": "open",
  "priority": "high",
  "assignee": "john_doe",
  "description": "Fix critical bug in authentication..."
}
```

### Ticket Detail
```json
{
  "id": 1,
  "title": "Fix critical bug in authentication",
  "status": "open", 
  "priority": "high",
  "assignee": "john_doe",
  "description": "Fix critical bug in authentication...",
  "source_data": {
    "id": 1,
    "todo": "Fix critical bug in authentication",
    "completed": false,
    "userId": 1
  }
}
```

## Data Transformation

The service transforms DummyJSON todos into tickets using the following rules:

- **ID**: Direct mapping from todo ID
- **Title**: From `todo` field
- **Status**: `closed` if `completed == true`, else `open`
- **Priority**: Calculated from `id % 3` → `0=low, 1=medium, 2=high`
- **Assignee**: Username from `userId` lookup
- **Description**: Truncated title (≤ 100 chars)

## Development

### Available Commands

```bash
make help          # Show all commands
make install       # Install dependencies
make dev           # Install dev dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make run           # Run development server
make docker-build  # Build Docker image
make docker-run    # Run with Docker Compose
make clean         # Clean cache files
```

### Code Quality

The project maintains high code quality standards:

- **Black** - Code formatting
- **isort** - Import sorting  
- **flake8** - Linting
- **mypy** - Type checking
- **pytest** - Testing with >90% coverage
- **bandit** - Security analysis

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
python -m pytest tests/test_api.py -v
```

## Architecture

### Project Structure
```
tickethub/
├── src/tickethub/           # Application code
│   ├── main.py             # FastAPI app and routes
│   ├── models.py           # Pydantic models
│   ├── service.py          # Business logic
│   ├── external_client.py  # DummyJSON client
│   ├── auth.py             # Authentication
│   └── cache.py            # Caching layer
├── tests/                  # Test suite
├── ci/                     # CI/CD configurations
├── docker-compose.yml      # Docker services
├── Dockerfile              # Container definition
├── Makefile               # Development commands
└── requirements.txt       # Dependencies
```

### External Dependencies

- **DummyJSON APIs**:
  - Tickets: https://dummyjson.com/todos
  - Users: https://dummyjson.com/users
  - Auth: https://dummyjson.com/auth/login

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONPATH` | `/app` | Python path for imports |
| `SECRET_KEY` | `...` | JWT secret (change in production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/auth/login` | 5/minute |
| `/health` | 30/minute |
| `/tickets` | 100/minute |
| `/tickets/search` | 50/minute |
| `/tickets/{id}` | 200/minute |
| `/stats` | 20/minute |


### Security Considerations

- Use HTTPS in production
- Configure proper CORS origins
- Monitor rate limits
- Regular security updates

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0",
  "uptime": 3600.0
}
```

### Metrics
- Application logs (INFO/WARNING/ERROR levels)
- Docker health checks
- API response times
- Rate limit violations

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run quality checks: `make ci-test`
5. Submit a pull request

## License

This project is licensed under the MIT License.