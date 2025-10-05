"""
Test de validación de contraseñas fuertes
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Agregar directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from tests.conftest import TEST_PASSWORDS

client = TestClient(app)


def test_password_validation_in_registration():
    """Test: Validación de contraseñas fuertes en registro"""
    # Primero necesitamos un token de admin
    login_response = client.post(
        "/auth/login",
        json={"username_or_email": "admin_test", "password": TEST_PASSWORDS["admin"]},
    )

    if login_response.status_code != 200:
        pytest.skip("Cannot get admin token for testing")

    admin_token = login_response.json()["access_token"]

    # Test 1: Contraseña débil debe fallar
    weak_password_response = client.post(
        "/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "test_weak_user",
            "email": "weak@test.com",
            "password": "123456",  # Contraseña débil
            "role_id": 3,
        },
    )

    print(f"Weak password response: {weak_password_response.status_code}")
    print(f"Weak password detail: {weak_password_response.json()}")

    # Debe fallar por contraseña débil
    assert (
        weak_password_response.status_code == 422
        or weak_password_response.status_code == 400
    )

    # Test 2: Contraseña fuerte debe funcionar
    strong_password_response = client.post(
        "/auth/register",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "test_strong_user",
            "email": "strong@test.com",
            "password": TEST_PASSWORDS["temp"],  # Contraseña fuerte
            "role_id": 3,
        },
    )

    print(f"Strong password response: {strong_password_response.status_code}")
    print(f"Strong password detail: {strong_password_response.json()}")

    # Debe funcionar con contraseña fuerte
    assert strong_password_response.status_code == 201


def test_strong_passwords_work():
    """Test: Verificar que las contraseñas fuertes de test funcionan"""

    # Test login con contraseñas fuertes
    for role, password in TEST_PASSWORDS.items():
        if role == "temp":
            continue

        username = f"{role}_test"

        response = client.post(
            "/auth/login", json={"username_or_email": username, "password": password}
        )

        print(f"Login {role}: {response.status_code}")
        if response.status_code != 200:
            print(f"Login failed for {role}: {response.json()}")

        assert response.status_code == 200, (
            f"Login failed for {role} with strong password"
        )
        assert "access_token" in response.json()


if __name__ == "__main__":
    print("🧪 Testing password validation...")

    # Test manual de las funciones
    print("\n1. Testing strong passwords login...")
    test_strong_passwords_work()
    print("✅ Strong passwords work!")

    print("\n2. Testing password validation in registration...")
    test_password_validation_in_registration()
    print("✅ Password validation works!")

    print("\n🎉 All password tests passed!")
