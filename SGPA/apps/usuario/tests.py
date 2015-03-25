from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
import SGPA

if not settings.configured:
    settings.configure(SGPA.apps, DEBUG=True)

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="Jose")

    def test_user_add(self):
        user = User.objects.get(name="Jose")
        self.assertEqual(user.get_username,'Jose')
