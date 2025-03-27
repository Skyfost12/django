import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase
from crud_user.models import Usuario
from crud_user.serializers import UsuarioSerializer

@pytest.mark.django_db
def test_user_creation_valid_data():
    user = Usuario.objects.create(
        nombre="Test Usuario",
        direccion="Calle Test 123",
        telefono="123456789",
        correo="test@example.com",
        genero="M",
        edad=30
    )
    assert user.id is not None
    assert user.nombre == "Test Usuario"
    assert user.correo == "test@example.com"

@pytest.mark.django_db
def test_user_creation_invalid_data():
    with pytest.raises(ValidationError):
        user = Usuario(
            nombre="",  
            direccion="Dirección",
            telefono="123456789",
            correo="invalid-email",  
            genero="X",  
            edad=-5  
        )
        user.full_clean()  

@pytest.mark.django_db
def test_user_serializer_valid_data():
    data = {
        "nombre": "Test Usuario",
        "direccion": "Calle Test 123",
        "telefono": "123456789",
        "correo": "test@example.com",
        "genero": "M",
        "edad": 30
    }
    serializer = UsuarioSerializer(data=data)
    assert serializer.is_valid()

@pytest.mark.django_db
def test_user_serializer_invalid_data():
    data = {
        "nombre": "", 
        "direccion": "Dirección",
        "telefono": "123456789",
        "correo": "invalid-email",  
        "genero": "X",  
        "edad": -5  
    }
    serializer = UsuarioSerializer(data=data)
    assert not serializer.is_valid()

@pytest.mark.django_db
def test_str_representation():
    user = Usuario.objects.create(
        nombre="Pepe Prueba",
        direccion="Calle Test 123",
        telefono="123456789",
        correo="pepe@example.com",
        genero="M",
        edad=30
    )
    assert str(user) == "Pepe Prueba"

@pytest.mark.django_db
def test_model_validation_genero():
    with pytest.raises(ValidationError):
        user = Usuario(
            nombre="User Test",
            direccion="Dirección Test",
            telefono="123456789",
            correo="user@test.com",
            genero="X", 
            edad=30
        )
        user.full_clean()

@pytest.mark.django_db
def test_model_validation_edad():
    usuario = Usuario.objects.create(
        nombre="User Test",
        direccion="Dirección Test",
        telefono="123456789",
        correo="edad@test.com",
        genero="M",
        edad=25  
    )
    assert usuario.edad == 25

@pytest.mark.django_db
def test_unique_email():
    Usuario.objects.create(
        nombre="Usuario Uno",
        direccion="Dirección 1",
        telefono="111222333",
        correo="duplicado@test.com",
        genero="M",
        edad=30
    )
    
    with pytest.raises(Exception):  
        Usuario.objects.create(
            nombre="Usuario Dos",
            direccion="Dirección 2",
            telefono="444555666",
            correo="duplicado@test.com", 
            genero="F",
            edad=25
        )

@pytest.mark.django_db
def test_model_defaults():
    with pytest.raises(Exception):
        Usuario.objects.create(
            nombre="Usuario Incompleto",
            telefono="123456789",
            correo="incompleto@test.com",
            genero="M",
        )