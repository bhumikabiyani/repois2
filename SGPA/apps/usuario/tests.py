from django.test import TestCase
from django.contrib.auth.models import User


import unittest

class SimplisticTest(unittest.TestCase):
    def test(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()

class UseraddTest(unittest.TestCase):
    def test(self):
        u = User()
        name = 'Jose'
        u.username = 'Jose'
        u.save