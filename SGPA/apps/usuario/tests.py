from django.test import TestCase
from django.contrib.auth.models import User


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="Jose")

    def test_user_add(self):
        user = User.objects.get(name="Jose")
        self.assertEqual(user.get_username,'Jose')
