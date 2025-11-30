from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

app = FastAPI(title="Person API", version="1.0.0")

# In-memory storage for persons
persons_db = {}


class Person(BaseModel):
    id: Optional[str] = None
    name: str
    age: int
    email: str


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Welcome to Person API. Visit /docs for API documentation."}


@app.post("/persons", response_model=Person, status_code=201)
def create_person(person: Person):
    """Create a new person"""
    person_id = str(uuid4())
    person.id = person_id
    persons_db[person_id] = person
    return person


@app.get("/persons", response_model=List[Person])
def get_all_persons():
    """Get all persons"""
    return list(persons_db.values())


@app.get("/persons/{person_id}", response_model=Person)
def get_person(person_id: str):
    """Get a specific person by ID"""
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    return persons_db[person_id]


@app.put("/persons/{person_id}", response_model=Person)
def update_person(person_id: str, person_update: PersonUpdate):
    """Update a person by ID"""
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    stored_person = persons_db[person_id]
    update_data = person_update.model_dump(exclude_unset=True)
    
    updated_person = stored_person.model_copy(update=update_data)
    persons_db[person_id] = updated_person
    
    return updated_person


@app.delete("/persons/{person_id}", status_code=204)
def delete_person(person_id: str):
    """Delete a person by ID"""
    if person_id not in persons_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    del persons_db[person_id]
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
