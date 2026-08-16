from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_inicio():
    response = client.get("/")
    assert response.status_code==200
    assert response.json() == {"mensaje": "Hola desde FastAPI!"}

def test_crear_pelicula():

    login_response = client.post("/login", data={"username": "Pau", "password": "PauCar1013+"})
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/peliculas", json={"titulo": "miaumiau", "año": 2024}, headers = headers)

    assert response.status_code == 200
    assert response.json()["titulo"] == "miaumiau"
    assert response.json()["año"] == 2024

