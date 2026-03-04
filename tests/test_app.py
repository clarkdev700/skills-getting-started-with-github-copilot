import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app, activities

# Copie de l'état initial des activités
import copy
initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Réinitialise l'état avant chaque test
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))

@pytest.mark.asyncio
async def test_get_activities():
    # Arrange
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

@pytest.mark.asyncio
async def test_signup_activity():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.post(f"/activities/{activity}/signup?email={email}")
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Act (doublon)
        response_dup = await ac.post(f"/activities/{activity}/signup?email={email}")
        # Assert
        assert response_dup.status_code == 400
        assert "already signed up" in response_dup.json()["detail"]

@pytest.mark.asyncio
async def test_signup_activity_not_found():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "NonExistentClub"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_signup_activity():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Arrange : inscrire le participant
        await ac.post(f"/activities/{activity}/signup?email={email}")
        # Act
        response = await ac.delete(f"/activities/{activity}/signup?email={email}")
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Act (désinscription email non inscrit)
        response_not_found = await ac.delete(f"/activities/{activity}/signup?email=notfound@mergington.edu")
        # Assert
        assert response_not_found.status_code == 400
        assert "not registered" in response_not_found.json()["detail"]

@pytest.mark.asyncio
async def test_delete_signup_activity_not_found():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "NonExistentClub"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
