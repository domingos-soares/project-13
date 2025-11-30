import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from main import app
from database import Base, get_db

# Use file-based SQLite for testing (to persist across connections)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with database override."""
    from fastapi import FastAPI
    
    # Create a new app instance without lifespan for testing
    test_app = FastAPI(title="Person API", version="1.0.0")
    
    # Import and register all routes from main app
    from main import Person, PersonUpdate, root, health_check, create_person, get_all_persons, get_person, update_person, delete_person
    
    test_app.add_api_route("/", root, methods=["GET"])
    test_app.add_api_route("/health", health_check, methods=["GET"])
    test_app.add_api_route("/persons", create_person, methods=["POST"], response_model=Person, status_code=201)
    test_app.add_api_route("/persons", get_all_persons, methods=["GET"], response_model=list[Person])
    test_app.add_api_route("/persons/{person_id}", get_person, methods=["GET"], response_model=Person)
    test_app.add_api_route("/persons/{person_id}", update_person, methods=["PUT"], response_model=Person)
    test_app.add_api_route("/persons/{person_id}", delete_person, methods=["DELETE"], status_code=204)
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    # Initialize the test database tables before each test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    # Clean up tables after each test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    test_app.dependency_overrides.clear()
