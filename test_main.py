import pytest
from fastapi.testclient import TestClient
from main import app, persons_db, Person, PersonUpdate


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the database before each test"""
    persons_db.clear()
    yield
    persons_db.clear()


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def sample_person():
    """Sample person data for testing"""
    return {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root(self, client):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Welcome to Person API. Visit /docs for API documentation."
        }


class TestCreatePerson:
    """Tests for POST /persons"""

    def test_create_person_success(self, client, sample_person):
        """Test creating a person successfully"""
        response = client.post("/persons", json=sample_person)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_person["name"]
        assert data["age"] == sample_person["age"]
        assert data["email"] == sample_person["email"]
        assert "id" in data
        assert data["id"] is not None

    def test_create_person_stores_in_db(self, client, sample_person):
        """Test that created person is stored in database"""
        response = client.post("/persons", json=sample_person)
        person_id = response.json()["id"]
        assert person_id in persons_db
        assert persons_db[person_id].name == sample_person["name"]

    def test_create_person_invalid_data_missing_field(self, client):
        """Test creating person with missing required field"""
        invalid_person = {"name": "John Doe", "age": 30}  # missing email
        response = client.post("/persons", json=invalid_person)
        assert response.status_code == 422

    def test_create_person_invalid_data_wrong_type(self, client):
        """Test creating person with wrong data type"""
        invalid_person = {"name": "John Doe", "age": "thirty", "email": "john@example.com"}
        response = client.post("/persons", json=invalid_person)
        assert response.status_code == 422

    def test_create_multiple_persons_unique_ids(self, client, sample_person):
        """Test that multiple persons get unique IDs"""
        response1 = client.post("/persons", json=sample_person)
        response2 = client.post("/persons", json=sample_person)
        id1 = response1.json()["id"]
        id2 = response2.json()["id"]
        assert id1 != id2


class TestGetAllPersons:
    """Tests for GET /persons"""

    def test_get_all_persons_empty(self, client):
        """Test getting all persons when database is empty"""
        response = client.get("/persons")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_persons_with_data(self, client, sample_person):
        """Test getting all persons when database has data"""
        # Create two persons
        client.post("/persons", json=sample_person)
        client.post("/persons", json={
            "name": "Jane Smith",
            "age": 25,
            "email": "jane@example.com"
        })
        
        response = client.get("/persons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("id" in person for person in data)
        assert all("name" in person for person in data)

    def test_get_all_persons_returns_list(self, client):
        """Test that get all persons returns a list"""
        response = client.get("/persons")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGetPerson:
    """Tests for GET /persons/{person_id}"""

    def test_get_person_success(self, client, sample_person):
        """Test getting a specific person successfully"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        response = client.get(f"/persons/{person_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == person_id
        assert data["name"] == sample_person["name"]
        assert data["age"] == sample_person["age"]
        assert data["email"] == sample_person["email"]

    def test_get_person_not_found(self, client):
        """Test getting a non-existent person returns 404"""
        response = client.get("/persons/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"

    def test_get_person_correct_data(self, client):
        """Test that retrieved person has all correct fields"""
        person_data = {"name": "Test User", "age": 40, "email": "test@example.com"}
        create_response = client.post("/persons", json=person_data)
        person_id = create_response.json()["id"]
        
        response = client.get(f"/persons/{person_id}")
        data = response.json()
        assert set(data.keys()) == {"id", "name", "age", "email"}


class TestUpdatePerson:
    """Tests for PUT /persons/{person_id}"""

    def test_update_person_full_update(self, client, sample_person):
        """Test updating all fields of a person"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        update_data = {
            "name": "Jane Smith",
            "age": 25,
            "email": "jane@example.com"
        }
        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["age"] == update_data["age"]
        assert data["email"] == update_data["email"]
        assert data["id"] == person_id

    def test_update_person_partial_update_name(self, client, sample_person):
        """Test updating only name field"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        update_data = {"name": "Updated Name"}
        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["age"] == sample_person["age"]
        assert data["email"] == sample_person["email"]

    def test_update_person_partial_update_age(self, client, sample_person):
        """Test updating only age field"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        update_data = {"age": 35}
        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 35
        assert data["name"] == sample_person["name"]
        assert data["email"] == sample_person["email"]

    def test_update_person_partial_update_email(self, client, sample_person):
        """Test updating only email field"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        update_data = {"email": "newemail@example.com"}
        response = client.put(f"/persons/{person_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
        assert data["name"] == sample_person["name"]
        assert data["age"] == sample_person["age"]

    def test_update_person_not_found(self, client):
        """Test updating a non-existent person returns 404"""
        update_data = {"name": "New Name"}
        response = client.put("/persons/nonexistent-id", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"

    def test_update_person_persists_in_db(self, client, sample_person):
        """Test that update persists in database"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        update_data = {"name": "Updated Name"}
        client.put(f"/persons/{person_id}", json=update_data)
        
        assert persons_db[person_id].name == "Updated Name"

    def test_update_person_empty_update(self, client, sample_person):
        """Test updating person with empty data (no changes)"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        response = client.put(f"/persons/{person_id}", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_person["name"]
        assert data["age"] == sample_person["age"]
        assert data["email"] == sample_person["email"]


class TestDeletePerson:
    """Tests for DELETE /persons/{person_id}"""

    def test_delete_person_success(self, client, sample_person):
        """Test deleting a person successfully"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        response = client.delete(f"/persons/{person_id}")
        assert response.status_code == 204
        assert response.text == ""

    def test_delete_person_removes_from_db(self, client, sample_person):
        """Test that deleted person is removed from database"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        client.delete(f"/persons/{person_id}")
        assert person_id not in persons_db

    def test_delete_person_not_found(self, client):
        """Test deleting a non-existent person returns 404"""
        response = client.delete("/persons/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Person not found"

    def test_delete_person_verify_removed(self, client, sample_person):
        """Test that deleted person cannot be retrieved"""
        create_response = client.post("/persons", json=sample_person)
        person_id = create_response.json()["id"]
        
        client.delete(f"/persons/{person_id}")
        get_response = client.get(f"/persons/{person_id}")
        assert get_response.status_code == 404


class TestPersonModel:
    """Tests for Person and PersonUpdate models"""

    def test_person_model_with_id(self):
        """Test creating Person model with ID"""
        person = Person(id="test-id", name="John", age=30, email="john@example.com")
        assert person.id == "test-id"
        assert person.name == "John"
        assert person.age == 30
        assert person.email == "john@example.com"

    def test_person_model_without_id(self):
        """Test creating Person model without ID"""
        person = Person(name="John", age=30, email="john@example.com")
        assert person.id is None
        assert person.name == "John"

    def test_person_update_model_partial(self):
        """Test PersonUpdate model with partial data"""
        update = PersonUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.age is None
        assert update.email is None

    def test_person_update_model_full(self):
        """Test PersonUpdate model with all fields"""
        update = PersonUpdate(name="New Name", age=35, email="new@example.com")
        assert update.name == "New Name"
        assert update.age == 35
        assert update.email == "new@example.com"

    def test_person_update_model_empty(self):
        """Test PersonUpdate model with no fields"""
        update = PersonUpdate()
        assert update.name is None
        assert update.age is None
        assert update.email is None


class TestIntegrationScenarios:
    """Integration tests for common scenarios"""

    def test_full_crud_cycle(self, client, sample_person):
        """Test complete CRUD cycle for a person"""
        # Create
        create_response = client.post("/persons", json=sample_person)
        assert create_response.status_code == 201
        person_id = create_response.json()["id"]
        
        # Read
        get_response = client.get(f"/persons/{person_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == sample_person["name"]
        
        # Update
        update_response = client.put(f"/persons/{person_id}", json={"age": 31})
        assert update_response.status_code == 200
        assert update_response.json()["age"] == 31
        
        # Delete
        delete_response = client.delete(f"/persons/{person_id}")
        assert delete_response.status_code == 204
        
        # Verify deletion
        verify_response = client.get(f"/persons/{person_id}")
        assert verify_response.status_code == 404

    def test_multiple_persons_operations(self, client):
        """Test operations with multiple persons"""
        # Create multiple persons
        person1 = client.post("/persons", json={
            "name": "Person 1", "age": 20, "email": "p1@example.com"
        }).json()
        person2 = client.post("/persons", json={
            "name": "Person 2", "age": 30, "email": "p2@example.com"
        }).json()
        person3 = client.post("/persons", json={
            "name": "Person 3", "age": 40, "email": "p3@example.com"
        }).json()
        
        # Get all persons
        all_persons = client.get("/persons").json()
        assert len(all_persons) == 3
        
        # Delete one person
        client.delete(f"/persons/{person2['id']}")
        
        # Verify count
        remaining_persons = client.get("/persons").json()
        assert len(remaining_persons) == 2
        
        # Verify specific persons still exist
        assert client.get(f"/persons/{person1['id']}").status_code == 200
        assert client.get(f"/persons/{person3['id']}").status_code == 200
        assert client.get(f"/persons/{person2['id']}").status_code == 404
