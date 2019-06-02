import unittest
from wallhavenapi import WallhavenApiV1, Category, Purity, Sorting, Order, TopRange, Color, Type
import os
import datetime


class TestWallhavenApiV1(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.wallhaven_api = WallhavenApiV1(api_key=os.getenv('APIKEY', None), verify_connection=False, 
                                            base_url="http://wallhaven.cc/api/v1")
    
    def test_search(self):
        search_data = self.wallhaven_api.search()

        self.assertIn("data", search_data)
        self.assertIn("meta", search_data)

    def test_search_categories(self):
        for category in list(Category):
            search_data = self.wallhaven_api.search(categories=category)

            for wallpaper_data in search_data["data"]:
                self.assertEqual(category.value, wallpaper_data["category"])

    def test_search_purities(self):
        for purity in list(Purity):
            search_data = self.wallhaven_api.search(purities=purity)

            for wallpaper_data in search_data["data"]:
                self.assertEqual(purity.value, wallpaper_data["purity"])

    def test_search_sorting(self):
        for sorting_method in list(Sorting):
            search_data = self.wallhaven_api.search(sorting=sorting_method)
            self.assertIn("data", search_data)

    def search_sorting_dated_added(self, order):
        def parse_datetime(datetime_string):
            # Format: 2018-10-31 01:23:10.000000
            return datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S.%f")
        
        search_data = self.wallhaven_api.search(sorting=Sorting.date_added, order=order)
        for i in range(len(search_data["data"]) - 1):
            datetime_1 = parse_datetime(search_data["data"][i]["created_at"]["date"])
            datetime_2 = parse_datetime(search_data["data"][i + 1]["created_at"]["date"])
            self.assertGreaterEqual(datetime_1, datetime_2) \
            if order == Order.desc else self.assertLessEqual(datetime_1, datetime_2)

    def test_search_sorting_dated_added_asc(self):
        self.search_sorting_dated_added(Order.asc)

    def test_search_sorting_dated_added_desc(self):
        self.search_sorting_dated_added(Order.desc)

    def search_sorting_views(self, order):
        search_data = self.wallhaven_api.search(sorting=Sorting.views, order=order)
        for i in range(len(search_data["data"]) - 1):
            views_1 = int(search_data["data"][i]["views"])
            views_2 = int(search_data["data"][i + 1]["views"])
            self.assertGreaterEqual(views_1, views_2) \
            if order == Order.desc else self.assertLessEqual(views_1, views_2)

    @unittest.skip("http://stest39.wallhaven.cc/forums/thread/11")
    def test_search_sorting_views_asc(self):
        self.search_sorting_views(Order.asc)

    @unittest.skip("http://stest39.wallhaven.cc/forums/thread/11")
    def test_search_sorting_views_desc(self):
        self.search_sorting_views(Order.desc)

    def search_sorting_favorites(self, order):
        search_data = self.wallhaven_api.search(sorting=Sorting.favorites, order=order)
        for i in range(len(search_data["data"]) - 1):
            favorites_1 = int(search_data["data"][i]["favorites"])
            favorites_2 = int(search_data["data"][i + 1]["favorites"])
            self.assertGreaterEqual(favorites_1, favorites_2) \
            if order == Order.desc else self.assertLessEqual(favorites_1, favorites_2)

    def test_search_sorting_favorites_asc(self):
        self.search_sorting_favorites(Order.asc)

    def test_search_sorting_favorites_desc(self):
        self.search_sorting_favorites(Order.desc)
    
    def test_search_top_range(self):
        for top_range in list(TopRange):
            search_data = self.wallhaven_api.search(top_range=top_range, sorting=Sorting.toplist)
            self.assertIn("data", search_data)

            if str(top_range.value[-1]).endswith("d"):
                timedelta = datetime.timedelta(days=int(top_range.value[:-1]))
            elif str(top_range.value[-1]).endswith("w"):
                timedelta = datetime.timedelta(days=(int(top_range.value[:-1]) * 7))
            elif str(top_range.value[-1]).endswith("M"):
                timedelta = datetime.timedelta(days=(int(top_range.value[:-1]) * 30))
            else:
                timedelta = datetime.timedelta(days=(int(top_range.value[:-1]) * 365))

            for wallpaper in search_data["data"]:
                created_at = datetime.datetime.strptime(wallpaper["created_at"]["date"], "%Y-%m-%d %H:%M:%S.%f")

                self.assertGreaterEqual(created_at, datetime.datetime.now() - timedelta)
    
    def test_search_atleast(self):
        search_data = self.wallhaven_api.search(atleast=(1920, 1080))
        for wallpaper in search_data["data"]:
            self.assertGreaterEqual(int(wallpaper["dimension_x"]), 1920)
            self.assertGreaterEqual(int(wallpaper["dimension_y"]), 1080)

    def test_search_resolutions(self):
        search_data = self.wallhaven_api.search(resolutions=(1920, 1080))
        for wallpaper in search_data["data"]:
            self.assertEqual(int(wallpaper["dimension_x"]), 1920)
            self.assertEqual(int(wallpaper["dimension_y"]), 1080)

    def test_search_ratios(self):
        search_data = self.wallhaven_api.search(ratios=(16, 10))
        for wallpaper in search_data["data"]:
            self.assertEqual(float(wallpaper["ratio"]), 1.6)

    def test_search_colors(self):
        for color in list(Color):
            search_data = self.wallhaven_api.search(colors=color)
            for wallpaper in search_data["data"]:
                self.assertIn("colors", wallpaper)
                self.assertIn("#{}".format(color.value), wallpaper["colors"])

    def test_search_page(self):
        search_data = self.wallhaven_api.search()

        self.assertIn("last_page", search_data["meta"])

        if int(search_data["meta"]["last_page"]) > 1:
            search_data = self.wallhaven_api.search(page=2)

            self.assertIn("data", search_data)
            self.assertIn("meta", search_data)
            self.assertIn("current_page", search_data["meta"])
            self.assertEqual(2, int(search_data["meta"]["current_page"]))

    def test_wallpaper(self):
        search_data = self.wallhaven_api.search()

        if not len(search_data["data"]):
            return

        for wallpaper_temp in search_data["data"]:
            self.assertIn("id", wallpaper_temp)

        wallpaper = self.wallhaven_api.wallpaper(search_data["data"][0]["id"])
        self.assertIn("data", wallpaper)

    def test_tag(self):
        search_data = self.wallhaven_api.search()

        for wallpaper_temp in search_data["data"]:
            self.assertIn("id", wallpaper_temp)
            wallpaper = self.wallhaven_api.wallpaper(wallpaper_temp["id"])
            self.assertIn("data", wallpaper)
            self.assertIn("tags", wallpaper["data"])

            if not len(wallpaper["data"]["tags"]):
                continue

            for tag_temp in wallpaper["data"]["tags"]:
                self.assertIn("id", tag_temp)
        
            tag = self.wallhaven_api.tag(wallpaper["data"]["tags"][0]['id'])
            
            self.assertIn("data", tag)
            
            break

    def test_search_query_uploader(self):
        search_data = self.wallhaven_api.search()

        self.assertIn("data", search_data)

        if not len(search_data["data"]):
            return None

        wallpaper = self.wallhaven_api.wallpaper(search_data["data"][0]["id"])

        self.assertIn("data", wallpaper)
        self.assertIn("uploader", wallpaper["data"])
        self.assertIn("username", wallpaper["data"]["uploader"])
        
        search_data = self.wallhaven_api.search(q="@{}".format(wallpaper["data"]["uploader"]["username"]))

        self.assertIn("data", search_data)

        self.assertGreater(len(search_data["data"]), 0)

    def test_search_query_id(self):
        search_data = self.wallhaven_api.search()

        for wallpaper_temp in search_data["data"]:
            self.assertIn("id", wallpaper_temp)
            wallpaper = self.wallhaven_api.wallpaper(wallpaper_temp["id"])
            self.assertIn("data", wallpaper)
            self.assertIn("tags", wallpaper["data"])

            if not len(wallpaper["data"]["tags"]):
                continue

            for tag_temp in wallpaper["data"]["tags"]:
                self.assertIn("id", tag_temp)

            search_data = self.wallhaven_api.search(q="id:{}".format(wallpaper["data"]["tags"][0]['id']))
            
            self.assertIn("data", search_data)
            self.assertGreater(len(search_data["data"]), 0)
            break

    def test_search_query_like(self):
        search_data = self.wallhaven_api.search()

        if not len(search_data):
            return

        search_data = self.wallhaven_api.search(q="like:{}".format(search_data["data"][0]['id']))
            
        self.assertIn("data", search_data)
        self.assertIn("meta", search_data)

    def test_search_query_type(self):
        for image_type in Type:
            search_data = self.wallhaven_api.search(q="type:{}".format(image_type.value))
            
            self.assertIn("data", search_data)
            self.assertIn("meta", search_data)

            for wallpaper in search_data["data"]:
                self.assertIn("file_type", wallpaper)
                if image_type in [Type.jpeg, Type.jpg]:
                    self.assertTrue(str(wallpaper["file_type"]).endswith(Type.jpeg.value) \
                                    or str(wallpaper["file_type"]).endswith(Type.jpg.value))
                else:
                    self.assertTrue(str(wallpaper["file_type"]).endswith(image_type.value))

if __name__ == '__main__':
    unittest.main()