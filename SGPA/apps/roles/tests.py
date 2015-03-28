from django.test import TestCase
from django.test import RequestFactory
from SGPA.apps.roles.views import *
from django.contrib.messages.storage.fallback import FallbackStorage
import unittest
import django
django.setup()

class UserTestCase(TestCase):
    # def setUp(self):
    #     self.u1 = Rol.objects.create(nombre="admin")

    def testCreateRol_View(self):
        request = RequestFactory().get('/roles')
        rol = Rol.objects.get(nombre="admin")
        response = crear_rol(request)
        # Check.
        self.assertEqual(response.status_code, 100)

    def testCreateRol_View(self):
        user = User.objects.get(username="cgonza")
        self.assertEqual(user.get_username(),"cgonza")

    def testAdminRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = admin_roles(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testAdminRolSys_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = admin_roles_sist(request,"2")
        # Check.
        self.assertEqual(response.status_code, 200)

    def testViewRoles_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = visualizar_roles(request,"1")
        # Check.
        self.assertEqual(response.status_code, 302)

    def testModRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = mod_rol(request,"1")
        # Check.
        self.assertEqual(response.status_code, 302)

    def testAsigRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = user
        response = asignar_roles_sistema(request,"1")
        # Check.
        self.assertEqual(response.status_code, 200)


    def testDelRol_View(self):
        request = RequestFactory().get('/usuario')
        user = User.objects.get(username="cgonza")
        request.user = user
        response = borrar_rol(request)
        # Check.
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
