import unittest
import WallhavenApi
import os


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

    def test_get_image_data(self):
        data = self.wa.get_image_data("329194")

        self.assertIn("Category", data)
        self.assertIsNotNone(data["Category"])
        self.assertEqual(data["Category"], self.wa.get_image_category("329194"))

        self.assertIn("ShortUrl", data)
        self.assertIsNotNone(data["ShortUrl"])
        self.assertEqual(data["ShortUrl"], self.wa.get_image_short_url("329194"))

        self.assertIn("UploadTime", data)
        self.assertIsNotNone(data["UploadTime"])
        self.assertEqual(data["UploadTime"], self.wa.get_image_upload_time("329194"))

        self.assertIn("Ratio", data)
        self.assertIsNotNone(data["Ratio"])
        self.assertEqual(data["Ratio"], self.wa.get_image_ratio("329194"))

        self.assertIn("Resolution", data)
        self.assertIsNotNone(data["Resolution"])
        self.assertEqual(data["Resolution"], self.wa.get_image_resolution("329194"))

        self.assertIn("ImageColors", data)
        self.assertIsNotNone(data["ImageColors"])
        self.assertSequenceEqual(data["ImageColors"], self.wa.get_image_colors("329194"))

        self.assertIn("Favorites", data)
        self.assertIsNotNone(data["Favorites"])
        self.assertEqual(data["Favorites"], self.wa.get_image_favorites("329194"))

        self.assertIn("ImageUrl", data)
        self.assertIsNotNone(data["ImageUrl"])
        self.assertEqual(data["ImageUrl"], self.wa.get_image_url("329194"))

        self.assertIn("Size", data)
        self.assertIsNotNone(data["Size"])
        self.assertEqual(data["Size"], self.wa.get_image_size("329194"))

        self.assertIn("Purity", data)
        self.assertIsNotNone(data["Purity"])
        self.assertEqual(data["Purity"], self.wa.get_image_purity("329194"))

        self.assertIn("Views", data)
        self.assertIsNotNone(data["Views"])
        self.assertEqual(data["Views"], self.wa.get_image_views("329194"))

        self.assertIn("TagsEx", data)
        self.assertIsNotNone(data["TagsEx"])

        tags_ex = sorted(self.wa.get_image_tags_ex("329194"), key=lambda k: k['Id'])
        data["TagsEx"] = sorted(data["TagsEx"], key=lambda k: k['Id'])
        self.assertEqual(len(tags_ex), len(data["TagsEx"]))
        for i in range(0, len(tags_ex)):
            self.assertDictEqual(tags_ex[i], data["TagsEx"][i])

    def test_get_get_images_numbers(self):
        self.assertGreater(len(self.wa.get_images_numbers()), 0)

    def test_download_image(self):
        self.assertTrue(self.wa.download_image("329194", "tempfile.jpg"))
        os.remove("tempfile.jpg")

    def test_get_image_puruty_nsfw(self):
        self.assertIsNotNone(self.wa.get_image_purity("166969"))

    def test_image_tag_actions(self):
        tags = self.wa.get_image_tags_ex("329194")
        if len(tags):
            self.assertTrue(self.wa.image_tag_delete("329194", tags[0]["Id"]))
            self.assertTrue(self.wa.image_tag_add("329194", tags[0]["Name"]))
        else:
            self.assertTrue(False)

    def test_image_change_purity(self):
        self.assertTrue(self.wa.image_change_purity("329194", "sfw"))
        self.assertTrue(self.wa.image_change_purity("329194", "sketchy"))

if __name__ == '__main__':
    unittest.main()