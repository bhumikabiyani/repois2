from django.test import TestCase
# from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from SGPA.apps.home.views import *
from SGPA.apps.proyectos.views import *
from SGPA.apps.roles.views import *
from SGPA.apps.usuario.views import *
from SGPA.apps.flujo.views import *
import unittest
import django
django.setup()

class UserTestCase(TestCase):

    def setUp(self):
        self.u1 = User.objects.create(username="cgonza",first_name="Carlos",last_name="Gonzalez",email="cgonzalez@gmail.com")

    def testLogin_View(self):
        request = RequestFactory().get('/usuario')
        request.user = self.u1
        response = login_view(request)
        # Check.
        self.assertEqual(response.status_code, 302)

    def testRecuperarPass_View(self):
        request = RequestFactory().get('/usuario')
        response = recuperarcontrasena_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCreateRolSist_View(self):
        request = RequestFactory().get('/roles')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_rolS(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCreateRolProy_View(self):
        request = RequestFactory().get('/roles')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_rolP(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAdminRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = admin_roles(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="admin")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = mod_rol(request,"1")
        # Check.
        self.assertEqual(response.status_code, 200)


    def testDelRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = borrar_rol(request, '2')
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCreateUser(self):
        user = User.objects.get(username="cgonza")
        self.assertEqual(user.get_username(),"cgonza")


    def testAddUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crearUsuario_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = mod_user(request,"1")
        # Check.
        self.assertEqual(response.status_code, 200)

    def testDelUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = eliminar_usuario(request,"1")
        # Check.
        self.assertEqual(response.status_code, 302)

    def testUnDelUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = activar_usuario(request,"1")
        # Check.
        self.assertEqual(response.status_code, 302)

    def testViewUser_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = visualizar_usuario(request,"1")
        # Check.
        self.assertEqual(response.status_code, 200)

    def testChangePass_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = cambiar_password(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCrearProyecto_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_proyecto(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModProyecto_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        proy = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = mod_proyecto(request,proy.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAsigMiembro_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        proy = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = asignar_miembro(request,proy.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAsigFlujo_View(self):
        request = RequestFactory().get('/proyectos')
        user = User.objects.get(username="cgonza")
        proy = Proyecto.objects.get(nombrelargo="prueba")
        request.user = user
        response = asignar_flujo(request,proy.id)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testCrearFlujo_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = crear_flujo(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testModFlujo_View(self):
        request = RequestFactory().get('/flujos')
        user = User.objects.get(username="cgonza")
        flujo = Flujo.objects.get(nombre="prueba")
        request.user = user
        response = mod_flujo(request,flujo.id)
        # Check.
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()