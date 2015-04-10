from django.test import TestCase
# from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from SGPA.apps.home.views import *
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
        self.assertEqual(response.status_code, 200)

    # def testLogout_View(self):
    #     request = RequestFactory().get('/usuario')
    #     setattr(request, 'session', 'session')
    #     response = logout_view(request)
    #     # Check.
    #     self.assertEqual(response.status_code, 200)

    def testRecuperarPass_View(self):
        request = RequestFactory().get('/usuario')
        response = recuperarcontrasena_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    # def testNewPass_View(self):
    #     request = RequestFactory().get('/usuario')
    #     response = generar_nuevo_pass(request,"jorgek@gmail.com")
    #     # Check.
    #     self.assertEqual(response, None)

if __name__ == "__main__":
    unittest.main()