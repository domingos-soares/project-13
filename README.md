# project-13
Person REST API with FastAPI

## Description
A REST API server built with Python and FastAPI to manage Person objects with full CRUD operations.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload
```

The server will run on `http://localhost:8000`

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
