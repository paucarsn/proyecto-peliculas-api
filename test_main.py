from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_inicio():
    response = client.get("/")
    assert response.status_code==200
    assert response.json() == {"mensaje": "Hola desde FastAPI!"}

def test_crear_pelicula():

    login_response = client.post(
        "/login",
        data={"username": "Pau", "password": "PauCar1013+"}
    )

    print("STATUS:", login_response.status_code)
    print("RESPONSE:", login_response.json())

    token = login_response.json()["access_token"]


def test_crear_pelicula():
    login_response = client.post(
        "/login",
        data={"username": "Pau", "password": "PauCar1013+"}
    )

    print("STATUS:", login_response.status_code)
    print("RESPONSE:", login_response.json())

    assert login_response.status_code == 200