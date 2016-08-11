import unittest
import WallhavenApi


class TestClassInitLogin(unittest.TestCase):
    def test_class_init_login(self):
        wa = WallhavenApi.WallhavenApi(username='cufocufoma', password="cufocufoma@lackmail.ru")
        self.assertTrue(wa.logged_in)

class TestClassLogin(unittest.TestCase):
    def test_class_login(self):
        wa = WallhavenApi.WallhavenApi()
        self.assertTrue(wa.login(username='cufocufoma', password="cufocufoma@lackmail.ru"))


class TestLoggedUser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wa = WallhavenApi.WallhavenApi(username='cufocufoma', password="cufocufoma@lackmail.ru")

    def test_login(self):
        self.assertTrue(self.wa.login())

    def test_logout(self):
        self.assertTrue(self.wa.logout())
        self.wa.login()

    def test_get_pages_count(self):
        self.assertIsNotNone(self.wa.get_pages_count())

if __name__ == '__main__':
    unittest.main()