from django.test import TestCase
from django.contrib.auth.models import User
import unittest
import django
django.setup()

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="Carlos")

    def test_user_add(self):
        user = User.objects.get(username="Carlos")
        self.assertEqual(user.get_username(),"Carlos")

if __name__ == "__main__":
    unittest.main()