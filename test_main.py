from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_crear_pelicula():

    login_response = client.post(
        "/login",
        data={"username": "Pau", "password": "PauCar1013+"}
    )

    print("STATUS:", login_response.status_code)
    print("RESPONSE:", login_response.json())

    token = login_response.json()["access_token"]


def test_crear_producto():
    login_response = client.post(
        "/login",
        data={"username": "Pau", "password": "PauCar1013+"}
    )

    print("STATUS:", login_response.status_code)
    print("RESPONSE:", login_response.json())

    assert login_response.status_code == 200
    