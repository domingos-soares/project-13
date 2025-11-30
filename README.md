# project-13
Person REST API with FastAPI

## Description
A REST API server built with Python, FastAPI, and PostgreSQL to manage Person objects with full CRUD operations.

## Features
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ PostgreSQL database with SQLAlchemy async ORM
- ✅ Async/await support throughout
- ✅ Docker Compose for easy PostgreSQL setup
- ✅ Comprehensive test suite with 94% coverage
- ✅ Auto-generated API documentation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env if you need to change database connection settings
```

## Database Setup

### Option 1: Using Docker (Recommended)

Start PostgreSQL using Docker Compose:
```bash
docker-compose up -d
```

This will start a PostgreSQL server on port 5432 with:
- Database: `persons_db`
- User: `postgres`
- Password: `postgres`

### Option 2: Using an existing PostgreSQL instance

Update the `DATABASE_URL` in your `.env` file:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/your_database
```

## Running the Server

The database tables will be created automatically on startup.

Start the server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The server will run on `http://localhost:8000`

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage report:
```bash
pytest --cov=main --cov-report=term-missing
```

Run tests with HTML coverage report:
```bash
pytest --cov=main --cov-report=html
```

Current test coverage: **94%** (30 tests, all passing)

**Note**: Tests use SQLite for speed. PostgreSQL is used in production.

## API Documentation

Once the server is running, visit:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Available Routes

### POST /persons
Create a new person
```bash
curl -X POST http://localhost:8000/persons \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
```

### GET /persons
Get all persons
```bash
curl http://localhost:8000/persons
```

### GET /persons/{person_id}
Get a specific person by ID
```bash
curl http://localhost:8000/persons/{person_id}
```

### PUT /persons/{person_id}
Update a person by ID
```bash
curl -X PUT http://localhost:8000/persons/{person_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "age": 31}'
```

### DELETE /persons/{person_id}
Delete a person by ID
```bash
curl -X DELETE http://localhost:8000/persons/{person_id}
```

## Person Model

```json
{
  "id": "string (auto-generated)",
  "name": "string",
  "age": "integer",
  "email": "string"
}
```
