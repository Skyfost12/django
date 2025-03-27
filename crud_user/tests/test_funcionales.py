import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from crud_user.models import Usuario
import time

class UserCRUDUITest(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
       
        chrome_options.add_argument("--window-size=1920,1080")
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def test_user_create_form(self):        
        crear_url = reverse('crear_usuario')
        self.selenium.get(f"{self.live_server_url}{crear_url}")
             
        self.selenium.find_element(By.NAME, "nombre").send_keys("Usuario Prueba")
        self.selenium.find_element(By.NAME, "direccion").send_keys("Dirección Prueba")
        self.selenium.find_element(By.NAME, "telefono").send_keys("123456789")
        self.selenium.find_element(By.NAME, "correo").send_keys("prueba@test.com")
               
        genero_select = Select(self.selenium.find_element(By.NAME, "genero"))
        genero_select.select_by_value("M")
        
        self.selenium.find_element(By.NAME, "edad").send_keys("30")
                
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.selenium.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1) 
        self.selenium.execute_script("arguments[0].click();", submit_button)
                
        WebDriverWait(self.selenium, 10).until(
            lambda driver: "crear_usuario" not in driver.current_url.lower()
        )
    
    def test_user_edit_form(self):       
        usuario = Usuario.objects.create(
            nombre="Usuario Editable",
            direccion="Dirección Original",
            telefono="111222333",
            correo="editable@test.com",
            genero="M",
            edad=40
        )
        
        edit_url = reverse('editar_usuario', args=[usuario.id])
        self.selenium.get(f"{self.live_server_url}{edit_url}")
        
        nombre_input = self.selenium.find_element(By.NAME, "nombre")
        nombre_input.clear()
        nombre_input.send_keys("Usuario Editado")
                
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.selenium.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        self.selenium.execute_script("arguments[0].click();", submit_button)
        
        time.sleep(2)
        usuario.refresh_from_db()
        assert usuario.nombre == "Usuario Editado"
    
    def test_user_delete_confirmation(self):        
        usuario = Usuario.objects.create(
            nombre="Usuario Eliminable",
            direccion="Dirección a Eliminar",
            telefono="999888777",
            correo="eliminable@test.com",
            genero="F",
            edad=35
        )
        
        usuario_id = usuario.id
              
        delete_url = reverse('eliminar_usuario', args=[usuario.id])
        self.selenium.get(f"{self.live_server_url}{delete_url}")
                
        assert "confirmar" in self.selenium.page_source.lower() or "eliminar" in self.selenium.page_source.lower()
        
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.selenium.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        self.selenium.execute_script("arguments[0].click();", submit_button)
        
        time.sleep(3)
        
        from django.db.models.base import ObjectDoesNotExist
        
        try:
            Usuario.objects.get(id=usuario_id)
            deleted = False
        except ObjectDoesNotExist:
            deleted = True
        
        assert deleted, "El usuario no fue eliminado de la base de datos"
    
    def test_user_list_navigation(self):       
        Usuario.objects.create(
            nombre="Usuario Listado 1",
            direccion="Dirección Lista 1",
            telefono="111111111",
            correo="lista1@test.com",
            genero="M",
            edad=31
        )
        Usuario.objects.create(
            nombre="Usuario Listado 2",
            direccion="Dirección Lista 2",
            telefono="222222222",
            correo="lista2@test.com",
            genero="F",
            edad=32
        )
        
        list_url = reverse('lista_usuarios')
        self.selenium.get(f"{self.live_server_url}{list_url}")        
        
        page_content = self.selenium.page_source
        assert "Usuario Listado 1" in page_content
        assert "Usuario Listado 2" in page_content
    
    def test_form_validation_messages(self):
        crear_url = reverse('crear_usuario')
        self.selenium.get(f"{self.live_server_url}{crear_url}")
                
        initial_url = self.selenium.current_url
        initial_count = Usuario.objects.count()
        
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.selenium.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)
        self.selenium.execute_script("arguments[0].click();", submit_button)
                
        time.sleep(2)
                
        assert Usuario.objects.count() == initial_count
                
        assert "nuevo" in self.selenium.current_url.lower()
    
    def test_navigation_links(self):
        Usuario.objects.create(
            nombre="Usuario Nav", 
            direccion="Dir Nav",
            telefono="999999999",
            correo="nav@test.com",
            genero="M",
            edad=30
        )        
        
        list_url = reverse('lista_usuarios')
        self.selenium.get(f"{self.live_server_url}{list_url}")
                
        page_source = self.selenium.page_source.lower()
        has_create_link = (
            len(self.selenium.find_elements(By.XPATH, "//a[contains(@href, 'nuevo') or contains(text(), 'Nuevo') or contains(text(), 'Crear') or contains(text(), 'agregar')]")) > 0 or
            "nuevo" in page_source or
            "crear" in page_source or
            "agregar" in page_source
        )
        
        has_action_links = (
            len(self.selenium.find_elements(By.XPATH, "//a[contains(@href, 'editar') or contains(@href, 'eliminar') or contains(text(), 'Edit') or contains(text(), 'Delete')]")) > 0 or
            "editar" in page_source or
            "eliminar" in page_source
        )
    
        assert has_create_link or has_action_links
    
    def test_responsive_layout(self):        
        list_url = reverse('lista_usuarios')
        self.selenium.get(f"{self.live_server_url}{list_url}")        
        
        main_container = self.selenium.find_elements(By.TAG_NAME, "body")
        assert len(main_container) > 0
                
        assert "django" in self.selenium.page_source.lower() or "crud" in self.selenium.page_source.lower()