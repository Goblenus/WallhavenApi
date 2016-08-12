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

    def test_get_image_uploader(self):
        uploader = self.wa.get_image_uploader("329194")
        self.assertIsNotNone(uploader["Username"])
        self.assertIsNotNone(uploader["Avatar"]["32"])
        self.assertIsNotNone(uploader["Avatar"]["200"])

    def test_get_image_category(self):
        self.assertIsNotNone(self.wa.get_image_category("329194"))

    def test_get_image_short_url(self):
        self.assertIsNotNone(self.wa.get_image_short_url("329194"))

    def test_get_image_upload_time(self):
        self.assertIsNotNone(self.wa.get_image_upload_time("329194"))

    def test_get_image_ratio(self):
        self.assertIsNotNone(self.wa.get_image_ratio("329194"))

    def test_get_image_resolution(self):
        self.assertIsNotNone(self.wa.get_image_resolution("329194"))

    def test_get_image_colors(self):
        self.assertTrue(len(self.wa.get_image_colors("329194")) > 0)

    def test_get_image_favorites(self):
        self.assertIsNotNone(self.wa.get_image_favorites("329194"))

    def test_get_image_url(self):
        self.assertIsNotNone(self.wa.get_image_url("329194"))

    def test_get_image_size(self):
        self.assertIsNotNone(self.wa.get_image_size("329194"))

    def test_get_image_purity(self):
        self.assertIsNotNone(self.wa.get_image_purity("329194"))

    def test_get_image_views(self):
        self.assertIsNotNone(self.wa.get_image_views("329194"))

    def test_get_image_tags_ex(self):
        self.assertTrue(len(self.wa.get_image_tags_ex("329194")) > 0)

if __name__ == '__main__':
    unittest.main()