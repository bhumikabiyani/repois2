from django.test import TestCase
# from django.contrib.auth.models import User
from django.test import RequestFactory
from SGPA.apps.usuario.views import *
from django.contrib.messages.storage.fallback import FallbackStorage
import unittest
# import django
# django.setup()

class UserTestCase(TestCase):
    def setUp(self):
        self.u1 = User.objects.create(username="cgonza",first_name="Carlos",last_name="Gonzalez",email="cgonzalez@gmail.com")

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

if __name__ == "__main__":
    unittest.main()