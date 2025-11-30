from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from contextlib import asynccontextmanager

from database import get_db, init_db, PersonDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(title="Person API", version="1.0.0", lifespan=lifespan)

# Keep this for backwards compatibility with tests
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
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Person API. Visit /docs for API documentation."}


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    Returns the health status of the API and database
    """
    from datetime import datetime, timezone
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Person API",
        "version": "1.0.0"
    }
    
    # Check database connectivity
    try:
        # Simple query to test database connection
        await db.execute(select(1))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@app.post("/persons", response_model=Person, status_code=201)
async def create_person(person: Person, db: AsyncSession = Depends(get_db)):
    """Create a new person"""
    person_id = str(uuid4())
    person.id = person_id
    
    db_person = PersonDB(
        id=person_id,
        name=person.name,
        age=person.age,
        email=person.email
    )
    db.add(db_person)
    await db.commit()
    await db.refresh(db_person)
    
    return Person(
        id=db_person.id,
        name=db_person.name,
        age=db_person.age,
        email=db_person.email
    )


@app.get("/persons", response_model=List[Person])
async def get_all_persons(db: AsyncSession = Depends(get_db)):
    """Get all persons"""
    result = await db.execute(select(PersonDB))
    persons = result.scalars().all()
    return [
        Person(id=p.id, name=p.name, age=p.age, email=p.email)
        for p in persons
    ]


@app.get("/persons/{person_id}", response_model=Person)
async def get_person(person_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific person by ID"""
    result = await db.execute(select(PersonDB).where(PersonDB.id == person_id))
    db_person = result.scalar_one_or_none()
    
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return Person(
        id=db_person.id,
        name=db_person.name,
        age=db_person.age,
        email=db_person.email
    )


@app.put("/persons/{person_id}", response_model=Person)
async def update_person(
    person_id: str,
    person_update: PersonUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a person by ID"""
    result = await db.execute(select(PersonDB).where(PersonDB.id == person_id))
    db_person = result.scalar_one_or_none()
    
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    update_data = person_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_person, key, value)
    
    await db.commit()
    await db.refresh(db_person)
    
    return Person(
        id=db_person.id,
        name=db_person.name,
        age=db_person.age,
        email=db_person.email
    )


@app.delete("/persons/{person_id}", status_code=204)
async def delete_person(person_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a person by ID"""
    result = await db.execute(select(PersonDB).where(PersonDB.id == person_id))
    db_person = result.scalar_one_or_none()
    
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    await db.execute(delete(PersonDB).where(PersonDB.id == person_id))
    await db.commit()
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
