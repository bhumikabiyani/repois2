from django.test import TestCase
from django.contrib.auth.models import User
from django.test import RequestFactory
from SGPA.apps.usuario.views import *
import unittest
import django
django.setup()

class UserTestCase(TestCase):

    def testLogin_View(self):
        request = RequestFactory().get('/usuario')
        response = login_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testLogout_View(self):
        request = RequestFactory().get('/usuario')
        response = logout_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testRecuperarPass_View(self):
        request = RequestFactory().get('/usuario')
        response = recuperarcontrasena_view(request)
        # Check.
        self.assertEqual(response.status_code, 200)

    def testNewPass_View(self):
        request = RequestFactory().get('/usuario')
        response = generar_nuevo_pass(request)
        # Check.
        self.assertEqual(response.status_code, 200)

