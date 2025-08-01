from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_user():
    """Тест регистрации пользователя"""
    import uuid

    # Генерируем уникальные данные для теста
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"test{unique_id}@example.com",
        "username": f"testuser{unique_id}",
        "password": "Password123!",
    }

    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "uuid" in data
    assert "password" not in data


def test_login_user():
    """Тест входа пользователя"""
    import uuid

    # Генерируем уникальные данные для теста
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"test{unique_id}@example.com",
        "username": f"testuser{unique_id}",
        "password": "Password123!",
    }

    # Сначала регистрируем пользователя
    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201

    # Затем пытаемся войти
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"],
    }

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login():
    """Тест неверного входа"""
    login_data = {"email": "wrong@example.com", "password": "wrongpassword"}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_get_users():
    """Тест получения списка пользователей"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
