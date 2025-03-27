import pytest
from rest_framework.test import APIClient
from crud_user.models import Usuario
from django.urls import reverse

@pytest.mark.django_db
def test_create_user_api():
    client = APIClient()
    url = '/api/usuarios/'
    data = {
        "nombre": "Nuevo Usuario",
        "direccion": "Calle Nueva 456",
        "telefono": "987654321",
        "correo": "nuevo@example.com",
        "genero": "M",
        "edad": 28
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 201
    assert Usuario.objects.filter(correo="nuevo@example.com").exists()

@pytest.mark.django_db
def test_update_user_api():
    usuario = Usuario.objects.create(
        nombre="Usuario Original",
        direccion="Dirección Original",
        telefono="123456789",
        correo="original@example.com",
        genero="F",
        edad=35
    )
    
    client = APIClient()
    url = f'/api/usuarios/{usuario.id}/'
    data = {
        "nombre": "Usuario Actualizado",
        "direccion": "Dirección Actualizada"
    }
    
    response = client.patch(url, data, format='json')
    assert response.status_code == 200
    
    usuario.refresh_from_db()
    assert usuario.nombre == "Usuario Actualizado"
    assert usuario.direccion == "Dirección Actualizada"

# CASOS ADICIONALES

@pytest.mark.django_db
def test_delete_user_api():
    usuario = Usuario.objects.create(
        nombre="Usuario Eliminable",
        direccion="Dirección",
        telefono="123123123",
        correo="eliminable@test.com",
        genero="M",
        edad=40
    )
    
    client = APIClient()
    url = f'/api/usuarios/{usuario.id}/'
    
    response = client.delete(url)
    assert response.status_code == 204
    assert not Usuario.objects.filter(correo="eliminable@test.com").exists()

@pytest.mark.django_db
def test_get_user_list():
    # Crear varios usuarios para listar
    Usuario.objects.create(
        nombre="Usuario Uno",
        direccion="Dirección 1",
        telefono="111111111",
        correo="uno@test.com",
        genero="M",
        edad=31
    )
    Usuario.objects.create(
        nombre="Usuario Dos",
        direccion="Dirección 2",
        telefono="222222222",
        correo="dos@test.com",
        genero="F",
        edad=32
    )
    
    client = APIClient()
    url = '/api/usuarios/'
    
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 2
    assert any(user['correo'] == 'uno@test.com' for user in response.data)
    assert any(user['correo'] == 'dos@test.com' for user in response.data)

@pytest.mark.django_db
def test_get_user_detail():
    usuario = Usuario.objects.create(
        nombre="Usuario Detallado",
        direccion="Dirección Detalle",
        telefono="777888999",
        correo="detalle@test.com",
        genero="M",
        edad=45
    )
    
    client = APIClient()
    url = f'/api/usuarios/{usuario.id}/'
    
    response = client.get(url)
    assert response.status_code == 200
    assert response.data['nombre'] == "Usuario Detallado"
    assert response.data['correo'] == "detalle@test.com"

@pytest.mark.django_db
def test_invalid_update_api():
    usuario = Usuario.objects.create(
        nombre="Usuario Original",
        direccion="Dirección Original",
        telefono="123456789",
        correo="original2@example.com",
        genero="M",
        edad=35
    )
    
    client = APIClient()
    url = f'/api/usuarios/{usuario.id}/'
    data = {
        "correo": "invalid-email"  # Email inválido
    }
    
    response = client.patch(url, data, format='json')
    assert response.status_code == 400  # Bad request
    
    # Verificar que el usuario no fue actualizado
    usuario.refresh_from_db()
    assert usuario.correo == "original2@example.com"

@pytest.mark.django_db
def test_nonexistent_user_api():
    client = APIClient()
    # ID que no existe
    url = '/api/usuarios/99999/'
    
    response = client.get(url)
    assert response.status_code == 404  # Not found